from typing import List
import os
from .base import BaseChunker, Chunk

class LineChunker(BaseChunker):
    def __init__(self, max_lines: int = 100):
        self.max_lines = max_lines

    def chunk(self, file_content: str, file_path: str) -> List[Chunk]:
        lines = file_content.splitlines(keepends=True)
        chunks = []
        
        for i in range(0, len(lines), self.max_lines):
            chunk_lines = lines[i:i + self.max_lines]
            text = "".join(chunk_lines)
            chunks.append(Chunk(
                text=text,
                metadata={
                    "file": file_path,
                    "type": "text",
                    "name": f"{os.path.basename(file_path)}_{i//self.max_lines + 1}",
                    "start_line": i + 1,
                    "end_line": i + len(chunk_lines)
                }
            ))
            
        return chunks
