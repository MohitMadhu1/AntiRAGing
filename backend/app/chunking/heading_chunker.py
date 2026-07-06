import re
from typing import List
from .base import BaseChunker, Chunk

class HeadingChunker(BaseChunker):
    def chunk(self, file_content: str, file_path: str) -> List[Chunk]:
        # Split by markdown headers
        sections = re.split(r'(^#+\s+.*)', file_content, flags=re.MULTILINE)
        
        chunks = []
        current_heading = "Top"
        current_content = ""
        start_line = 1
        
        # sections[0] is everything before the first header
        if sections[0].strip():
            chunks.append(Chunk(
                text=sections[0],
                metadata={
                    "file": file_path,
                    "type": "markdown",
                    "name": current_heading,
                    "start_line": start_line,
                    "end_line": start_line + sections[0].count("\n")
                }
            ))
            start_line += sections[0].count("\n")
            
        for i in range(1, len(sections), 2):
            heading = sections[i]
            content = sections[i+1] if i+1 < len(sections) else ""
            
            full_section = heading + content
            line_count = full_section.count("\n")
            
            # Simple named extraction (remove # symbols)
            heading_name = re.sub(r'^#+\s+', '', heading).strip()
            
            chunks.append(Chunk(
                text=full_section,
                metadata={
                    "file": file_path,
                    "type": "markdown",
                    "name": heading_name,
                    "start_line": start_line,
                    "end_line": start_line + line_count
                }
            ))
            start_line += line_count
            
        return [c for c in chunks if c.text.strip()]
