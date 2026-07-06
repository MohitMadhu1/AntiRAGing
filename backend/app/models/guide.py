from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from app.database import Base
import uuid

class Guide(Base):
    __tablename__ = "guides"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), unique=True, nullable=False)
    architecture_section = Column(Text, nullable=True)
    modules_section = Column(Text, nullable=True)
    docs_health_section = Column(Text, nullable=True)
    getting_started_section = Column(Text, nullable=True)
    share_slug = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    from sqlalchemy.orm import relationship
    job = relationship("Job", lazy="joined")

    @property
    def repo_url(self):
        return self.job.repo_url if self.job else None
        
    @property
    def commit_sha(self):
        return self.job.commit_sha if self.job else None
