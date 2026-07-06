from pydantic import BaseModel
from datetime import datetime

class GuideResponse(BaseModel):
    id: str
    job_id: str
    architecture_section: str | None
    modules_section: str | None
    docs_health_section: str | None
    getting_started_section: str | None
    share_slug: str
    created_at: datetime
    repo_url: str | None = None
    commit_sha: str | None = None

    class Config:
        from_attributes = True
