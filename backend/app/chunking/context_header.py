def prepend_context(chunk_text: str, metadata: dict) -> str:
    """Prepends context headers to the chunk before embedding."""
    file_path = metadata.get("file", "unknown")
    module_name = metadata.get("module", "unknown")
    chunk_type = metadata.get("type", "unknown")
    name = metadata.get("name", "unknown")
    
    header = f"File: {file_path} | Module: {module_name} | Type: {chunk_type} | Name: {name}\n\n"
    return header + chunk_text
