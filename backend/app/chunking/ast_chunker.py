from typing import List, Dict, Any
import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_go as tsgo
import tree_sitter_java as tsjava
from .base import BaseChunker, Chunk

MAX_TOKENS = 150 # Heuristic for now, could use tiktoken
OVERLAP = 20

# Setup languages
LANGUAGES = {
    ".py": Language(tspython.language()),
    ".js": Language(tsjavascript.language()),
    ".ts": Language(tstypescript.language_typescript()),
    ".tsx": Language(tstypescript.language_tsx()),
    ".go": Language(tsgo.language()),
    ".java": Language(tsjava.language()),
}

QUERIES = {
    ".py": """
        (import_statement) @import
        (import_from_statement) @import
        (function_definition) @function
        (class_definition) @class
    """,
    ".js": """
        (import_statement) @import
        (function_declaration) @function
        (class_declaration) @class
    """,
    ".ts": """
        (import_statement) @import
        (function_declaration) @function
        (class_declaration) @class
    """,
    ".tsx": """
        (import_statement) @import
        (function_declaration) @function
        (class_declaration) @class
    """,
    ".go": """
        (import_spec) @import
        (function_declaration) @function
        (method_declaration) @method
        (type_declaration) @type
    """,
    ".java": """
        (import_declaration) @import
        (method_declaration) @method
        (class_declaration) @class
    """
}

class ASTChunker(BaseChunker):
    def chunk(self, file_content: str, file_path: str) -> List[Chunk]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in LANGUAGES or ext not in QUERIES:
            # Fallback
            from .line_chunker import LineChunker
            return LineChunker().chunk(file_content, file_path)
            
        lang = LANGUAGES[ext]
        parser = Parser(lang)
        tree = parser.parse(file_content.encode("utf-8"))
        
        query = lang.query(QUERIES[ext])
        captures = query.captures(tree.root_node)
        
        chunks = []
        file_imports = []
        
        # First pass: collect imports
        for node, tag in captures:
            if tag == "import":
                # Naive text extraction for imports, could be refined per language
                import_text = file_content[node.start_byte:node.end_byte]
                # Split by words and filter out common keywords
                words = import_text.replace(",", " ").replace(";", " ").split()
                clean_imports = [w for w in words if w not in ("import", "from", "as", "*")]
                file_imports.extend(clean_imports)
                
        # Deduplicate imports
        file_imports = list(set(file_imports))
        
        for node, tag in captures:
            if tag == "import":
                continue
                
            # Note: tree-sitter node structure varies by language. 
            # We attempt to find a 'name' node, or just use the tag.
            name_node = node.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else f"unnamed_{tag}"
            
            chunk_text = file_content[node.start_byte:node.end_byte]
            
            # Simple word count as token heuristic for splitting
            words = chunk_text.split()
            if len(words) > MAX_TOKENS:
                # Split large node
                step = MAX_TOKENS - OVERLAP
                for i in range(0, len(words), step):
                    window = words[i:i + MAX_TOKENS]
                    sub_text = " ".join(window)
                    chunks.append(Chunk(
                        text=sub_text,
                        metadata={
                            "file": file_path,
                            "type": tag,
                            "name": name,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "sub_chunk": i // step,
                            "imports": file_imports
                        }
                    ))
            else:
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={
                        "file": file_path,
                        "type": tag,
                        "name": name,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "imports": file_imports
                    }
                ))
                
        # If no captures found, fallback
        if not chunks:
            from .line_chunker import LineChunker
            return LineChunker().chunk(file_content, file_path)
            
        return chunks
