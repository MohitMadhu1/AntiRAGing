import os
from typing import List
from .base import Chunk
from .ast_chunker import ASTChunker
from .heading_chunker import HeadingChunker
from .line_chunker import LineChunker

AST_EXTS = {".py", ".ts", ".js", ".tsx", ".go", ".java"}
MD_EXTS = {".md", ".mdx"}

def chunk_file(file_content: str, file_path: str) -> List[Chunk]:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in AST_EXTS:
        return ASTChunker().chunk(file_content, file_path)
    elif ext in MD_EXTS:
        return HeadingChunker().chunk(file_content, file_path)
    else:
        return LineChunker().chunk(file_content, file_path)
