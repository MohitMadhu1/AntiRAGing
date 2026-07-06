import os

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__", ".venv", "venv", 
    "env", ".env", "coverage", ".idea", ".vscode", "target", "out"
}

SKIP_EXTS = {
    ".lock", ".min.js", ".map", ".png", ".jpg", ".jpeg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".pdf", ".mp4", ".mp3", ".wav", ".gif", ".svg", ".pyc"
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "poetry.lock", "pnpm-lock.yaml", "Pipfile.lock"
}

MAX_SIZE = 500 * 1024  # 500 KB limit for source files

def should_process(file_path: str, size: int) -> bool:
    if size > MAX_SIZE:
        return False
        
    filename = os.path.basename(file_path)
    if filename in SKIP_FILES:
        return False
        
    ext = os.path.splitext(filename)[1].lower()
    if ext in SKIP_EXTS:
        return False
        
    parts = file_path.replace("\\", "/").split("/")
    for part in parts:
        if part in SKIP_DIRS:
            return False
            
    return True
