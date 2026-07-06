from pydantic import BaseModel
from typing import List, Dict, Any

class Chunk(BaseModel):
    text: str
    metadata: Dict[str, Any]

class BaseChunker:
    def chunk(self, file_content: str, file_path: str) -> List[Chunk]:
        raise NotImplementedError
