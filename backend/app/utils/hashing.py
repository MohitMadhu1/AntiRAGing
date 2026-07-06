import hashlib

def hash_file_content(content: str) -> str:
    """Returns SHA-256 hash of the content string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
