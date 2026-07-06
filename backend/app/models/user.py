from sqlalchemy import Column, String, DateTime, func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)  # Nullable for GitHub users without public email
    hashed_password = Column(String, nullable=True) # Nullable for pure OAuth users
    github_id = Column(String, unique=True, index=True, nullable=True)
    github_access_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

