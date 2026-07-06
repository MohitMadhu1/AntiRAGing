from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.embedding import ChunkEmbedding
import uuid

class VectorService:
    @staticmethod
    async def save_chunks(session: AsyncSession, job_id: str, chunks_data: List[Dict[str, Any]]):
        """
        Saves a batch of chunks and their embeddings to pgvector.
        chunks_data format: [{"file_hash": str, "embedding": List[float], "metadata": dict}, ...]
        """
        embeddings = [
            ChunkEmbedding(
                id=str(uuid.uuid4()),
                job_id=job_id,
                file_hash=data["file_hash"],
                embedding=data["embedding"],
                metadata_json=data["metadata"]
            )
            for data in chunks_data
        ]
        session.add_all(embeddings)
        await session.commit()

    @staticmethod
    async def get_existing_embeddings_by_hashes(session: AsyncSession, file_hashes: List[str]) -> Dict[str, List[float]]:
        """
        Given a list of file hashes, queries pgvector to find any existing embeddings.
        Returns a dictionary mapping file_hash -> embedding.
        """
        if not file_hashes:
            return {}
            
        stmt = (
            select(ChunkEmbedding.file_hash, ChunkEmbedding.embedding)
            .where(ChunkEmbedding.file_hash.in_(file_hashes))
        )
        result = await session.execute(stmt)
        
        # Build dictionary. If multiple exist for same hash, one is fine.
        existing = {}
        for row in result:
            existing[row.file_hash] = row.embedding
            
        return existing

    @staticmethod
    async def query_similar(session: AsyncSession, job_id: str, query_embedding: List[float], limit: int = 6):
        """
        Queries pgvector for the most similar chunks based on cosine distance.
        """
        # <-> is L2 distance, <=> is cosine distance, <#> is inner product
        stmt = (
            select(ChunkEmbedding)
            .where(ChunkEmbedding.job_id == job_id)
            .order_by(ChunkEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_name(session: AsyncSession, job_id: str, name: str):
        """
        Queries for a specific chunk by its named entity (e.g., function name).
        Useful for the hybrid retrieval path.
        """
        # Filtering by jsonb metadata
        stmt = (
            select(ChunkEmbedding)
            .where(
                ChunkEmbedding.job_id == job_id,
                ChunkEmbedding.metadata_json['name'].astext == name
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()
