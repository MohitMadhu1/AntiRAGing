from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.database import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # Optional for anonymous MVP usage
    repo_url = Column(String, nullable=False)
    commit_sha = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued") # queued, processing, complete, failed
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
