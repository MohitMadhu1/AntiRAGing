from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.job import JobCreate, JobResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.models.user import User
from app.workers.ingestion_task import run_ingestion_job
from app.utils.security import get_current_user
from app.workers.progress import ProgressManager
import asyncio
import json
import uuid

router = APIRouter()

from sqlalchemy import select, desc

@router.post("/", response_model=JobResponse)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    new_job = Job(id=job_id, user_id=current_user.id, repo_url=str(job_in.repo_url), status="queued")
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Enqueue Celery Task
    run_ingestion_job.delay(job_id, str(job_in.repo_url), current_user.github_access_token)
    
    return new_job

@router.get("/", response_model=list[JobResponse])
async def get_jobs(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Job).where(Job.user_id == current_user.id).order_by(desc(Job.created_at)).limit(20)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return jobs

@router.get("/{job_id}/progress")
async def get_job_progress(job_id: str):
    async def event_generator():
        while True:
            progress = ProgressManager.get(job_id)
            if progress:
                # Format as Server-Sent Event
                yield f"data: {json.dumps(progress)}\n\n"
                
                # If job complete or failed, break
                if progress.get("status") in ["Complete", "Error", "failed"]:
                    break
                    
            await asyncio.sleep(0.5)
            
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)
