from sqlalchemy import Column, String, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid

class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, index=True, nullable=False) # Important for multi-tenant scoping
    file_hash = Column(String, index=True, nullable=False) # For caching
    embedding = Column(Vector(768)) # 768 is typical for Gemini/HuggingFace embeddings, adjust if needed
    metadata_json = Column(JSONB, nullable=False) # file, start_line, end_line, type, name, imports, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
