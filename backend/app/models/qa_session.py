from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
import uuid

class QASession(Base):
    __tablename__ = "qa_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guide_id = Column(String, ForeignKey("guides.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources_json = Column(JSONB, nullable=True) # Store array of cited sources
    created_at = Column(DateTime(timezone=True), server_default=func.now())
