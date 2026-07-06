from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class JobCreate(BaseModel):
    repo_url: HttpUrl
    # Could add branch or options here later

class JobResponse(BaseModel):
    id: str
    repo_url: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobProgress(BaseModel):
    agent: str
    status: str
    details: dict | None = None
