import os
import asyncio
from typing import List, Dict, Any
from app.workers.celery_app import celery_app
from app.workers.progress import ProgressManager
from app.services.github_service import GitHubService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.chunking.router import chunk_file
from app.chunking.context_header import prepend_context
from app.utils.file_filter import should_process
from app.utils.hashing import hash_file_content
from app.database import AsyncSessionLocal
from sqlalchemy import update
from app.models.job import Job
from app.agents.graph import create_onboarding_graph

from celery import chord, group

async def _prepare_ingestion_async(job_id: str, repo_url: str, github_token: str | None = None):
    ProgressManager.publish(job_id, "Ingestion Agent", "Initializing")
    
    repo_path = None
    try:
        # 1. Clone Repo
        ProgressManager.publish(job_id, "Ingestion Agent", "Cloning repository")
        repo_path = GitHubService.clone_repo(repo_url, github_token)
        commit_sha = GitHubService.get_latest_commit_sha(repo_path)
        
        # Update Job with commit SHA
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(commit_sha=commit_sha, status="processing")
            )
            await session.commit()
            
        # 2. Walk and filter files
        ProgressManager.publish(job_id, "Ingestion Agent", "Discovering files")
        valid_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    # Use relative path for should_process and display
                    rel_path = os.path.relpath(file_path, repo_path)
                    if should_process(rel_path, size):
                        valid_files.append((file_path, rel_path))
                except OSError:
                    continue
                    
        total_files = len(valid_files)
        if total_files == 0:
            raise ValueError("No readable code files found in this repository. Is it empty?")
        ProgressManager.publish(job_id, "Ingestion Agent", f"Found {total_files} files to process")
        
        # Bucket the files (e.g. 50 files per bucket)
        BUCKET_SIZE = 50
        buckets = [valid_files[i:i + BUCKET_SIZE] for i in range(0, len(valid_files), BUCKET_SIZE)]
        
        return repo_path, buckets
        
    except Exception as e:
        if repo_path:
            GitHubService.cleanup_repo(repo_path)
        raise e

@celery_app.task(bind=True)
def prepare_ingestion(self, job_id: str, repo_url: str, github_token: str | None = None):
    try:
        repo_path, buckets = asyncio.run(_prepare_ingestion_async(job_id, repo_url, github_token))
        
        # Launch celery chord
        # Create a group of tasks for each bucket
        bucket_tasks = group(process_file_bucket.s(bucket, job_id, repo_path) for bucket in buckets)
        
        # Chord runs the group, then calls aggregate_and_run_agents
        callback = aggregate_and_run_agents.s(job_id, repo_path)
        chord(bucket_tasks)(callback)
        
    except Exception as e:
        error_msg = str(e)
        ProgressManager.publish(job_id, "System", "Error", error=error_msg)
        async def _set_error():
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(Job).where(Job.id == job_id).values(status="failed", error_message=error_msg)
                )
                await session.commit()
        asyncio.run(_set_error())

async def _process_bucket_async(bucket: list, job_id: str, repo_path: str):
    all_chunks_data = []
    embedding_service = EmbeddingService()
    
    for abs_path, rel_path in bucket:
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            chunks = chunk_file(content, rel_path)
            
            for chunk in chunks:
                chunk.metadata["module"] = os.path.dirname(rel_path) or "root"
                text_with_context = prepend_context(chunk.text, chunk.metadata)
                
                chunk.metadata["text"] = text_with_context
                all_chunks_data.append({
                    "text": text_with_context,
                    "metadata": chunk.metadata,
                    "hash": hash_file_content(text_with_context)
                })
        except UnicodeDecodeError:
            pass
        except Exception as e:
            print(f"Error processing {rel_path}: {e}")
            
    # Batch Embeddings
    BATCH_SIZE = 50
    final_db_chunks = []
    
    for i in range(0, len(all_chunks_data), BATCH_SIZE):
        batch = all_chunks_data[i:i + BATCH_SIZE]
        
        batch_hashes = [c["hash"] for c in batch]
        async with AsyncSessionLocal() as session:
            cached_embeddings = await VectorService.get_existing_embeddings_by_hashes(session, batch_hashes)
            
        missing_chunks = []
        for c in batch:
            if c["hash"] in cached_embeddings:
                final_db_chunks.append({
                    "file_hash": c["hash"],
                    "embedding": cached_embeddings[c["hash"]],
                    "metadata": c["metadata"]
                })
            else:
                missing_chunks.append(c)
        
        if not missing_chunks:
            continue
            
        missing_texts = [c["text"] for c in missing_chunks]
        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = await embedding_service.get_embeddings(missing_texts)
                for c, emb in zip(missing_chunks, embeddings):
                    final_db_chunks.append({
                        "file_hash": c["hash"],
                        "embedding": emb,
                        "metadata": c["metadata"]
                    })
                await asyncio.sleep(4.5)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(15 * (attempt + 1))
                    else:
                        raise e
                else:
                    raise e
            
    # Save to pgvector directly from this worker
    async with AsyncSessionLocal() as session:
        await VectorService.save_chunks(session, job_id, final_db_chunks)

@celery_app.task(bind=True)
def process_file_bucket(self, bucket: list, job_id: str, repo_path: str):
    asyncio.run(_process_bucket_async(bucket, job_id, repo_path))
    return "done"

async def _aggregate_and_run_agents_async(job_id: str, repo_path: str):
    try:
        ProgressManager.publish(job_id, "LangGraph", "Starting Agents")
        graph = create_onboarding_graph()
        initial_state = {
            "job_id": job_id,
            "repo_path": repo_path,
            "architecture_overview": "",
            "key_modules": [],
            "docs_health": [],
            "getting_started": "",
            "env_vars": [],
            "guide_assembled": False
        }
        
        final_state = await graph.ainvoke(initial_state)
        
        ProgressManager.publish(job_id, "System", "Complete")
        
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="complete", completed_at=None)
            )
            await session.commit()
    except Exception as e:
        error_msg = str(e)
        ProgressManager.publish(job_id, "System", "Error", error=error_msg)
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="failed", error_message=error_msg)
            )
            await session.commit()
    finally:
        GitHubService.cleanup_repo(repo_path)

@celery_app.task(bind=True)
def aggregate_and_run_agents(self, results: list, job_id: str, repo_path: str):
    # results contains the return values of all process_file_bucket tasks
    asyncio.run(_aggregate_and_run_agents_async(job_id, repo_path))

# Keep the old function signature for compatibility during deploy, but route it
@celery_app.task(bind=True)
def run_ingestion_job(self, job_id: str, repo_url: str, github_token: str | None = None):
    prepare_ingestion.delay(job_id, repo_url, github_token)


