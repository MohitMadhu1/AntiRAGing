from pydantic import BaseModel
from typing import List

class SourceCitation(BaseModel):
    file: str
    start_line: int | None = None
    end_line: int | None = None
    type: str | None = None
    name: str | None = None

class QAAsk(BaseModel):
    guide_id: str
    question: str

class QAResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
