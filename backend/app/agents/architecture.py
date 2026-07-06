import os
from .state import OnboardingState
from google import genai
from app.config import settings

def run_architecture_agent(state: OnboardingState) -> dict:
    repo_path = state["repo_path"]
    
    # Expanded structural files list
    structural_files = {
        # Package managers & dependencies
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "package.json", "requirements.txt", "pyproject.toml",
        "Cargo.toml", "go.mod", "go.sum", "pom.xml", "build.gradle",
        "Gemfile", "composer.json",
        # Config & environment
        ".env.example", ".env.sample", "Makefile", "Procfile",
        "alembic.ini", "tsconfig.json", "vite.config.ts", "vite.config.js",
        "next.config.js", "next.config.mjs", "webpack.config.js",
        "nginx.conf", "vercel.json", "fly.toml", "render.yaml",
        # Documentation
        "README.md", "CONTRIBUTING.md", "ARCHITECTURE.md",
        # CI/CD (handled separately below)
    }
    
    context = ""
    
    # 1. Capture top-level directory listing for project shape
    try:
        top_level = os.listdir(repo_path)
        dirs = sorted([d for d in top_level if os.path.isdir(os.path.join(repo_path, d)) and not d.startswith(".")])
        files = sorted([f for f in top_level if os.path.isfile(os.path.join(repo_path, f))])
        context += "=== TOP-LEVEL DIRECTORY STRUCTURE ===\n"
        context += "Directories: " + ", ".join(dirs) + "\n"
        context += "Files: " + ", ".join(files) + "\n\n"
    except Exception:
        pass
    
    # 2. Read structural files (up to 3 levels deep)
    for root, dirnames, filenames in os.walk(repo_path):
        depth = root[len(repo_path):].count(os.sep)
        if depth > 3:
            continue
        # Skip noise directories
        dirnames[:] = [d for d in dirnames if d not in {
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            "dist", "build", ".next", ".tox", ".mypy_cache"
        }]
            
        for file in filenames:
            if file in structural_files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, repo_path)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()[:4000]
                    context += f"=== {rel_path} ===\n{content}\n\n"
                except Exception:
                    pass
                    
    # 3. Read CI/CD configs
    ci_dirs = [".github/workflows", ".gitlab-ci.yml", ".circleci"]
    for ci_dir in ci_dirs:
        ci_path = os.path.join(repo_path, ci_dir)
        if os.path.isdir(ci_path):
            for f in os.listdir(ci_path):
                if f.endswith((".yml", ".yaml")):
                    path = os.path.join(ci_path, f)
                    rel_path = os.path.relpath(path, repo_path)
                    try:
                        with open(path, "r", encoding="utf-8") as fh:
                            context += f"=== {rel_path} ===\n{fh.read()[:3000]}\n\n"
                    except Exception:
                        pass
        elif os.path.isfile(ci_path):
            rel_path = os.path.relpath(ci_path, repo_path)
            try:
                with open(ci_path, "r", encoding="utf-8") as fh:
                    context += f"=== {rel_path} ===\n{fh.read()[:3000]}\n\n"
            except Exception:
                pass
                
    if not context.strip():
        return {
            "architecture_overview": "No structural files found to analyze architecture.",
            "getting_started": "Run instructions not found.",
            "env_vars": []
        }

    prompt = f"""You are an expert software architect performing a thorough analysis of a codebase for a new developer onboarding guide.

Analyze ALL of the following infrastructure, configuration, and documentation files carefully:

{context}

Based on your analysis, produce a JSON object with the following keys. BE DETAILED AND THOROUGH — this is not a summary, it is a comprehensive architecture reference.

1. "architecture_overview": A DETAILED, multi-paragraph analysis (minimum 400 words) structured with these sub-topics:
   - **Tech Stack**: List every technology, framework, and language used. Be specific (e.g., "FastAPI 0.100+ with Pydantic v2" not just "Python").
   - **Project Structure**: Describe how the project is organized — what each top-level directory contains and how they relate.
   - **Services & Entry Points**: Identify the main application entry point(s), any background workers, and how they start.
   - **Databases & Storage**: What databases, caches, message queues, or object stores are used? How are they configured?
   - **Infrastructure & Deployment**: Docker setup, CI/CD pipelines, cloud platform targets, reverse proxies.
   - **Inter-Service Communication**: How do components talk to each other? REST, gRPC, message queues, SSE, WebSockets?
   
2. "getting_started": DETAILED step-by-step instructions to get this project running locally, written as numbered steps. Include:
   - Prerequisites (e.g., "Install Python 3.11+, Docker, Node.js 18+")
   - Environment setup (e.g., "Copy .env.example to .env and fill in values")
   - Dependency installation commands
   - Database setup / migration commands
   - How to start the application (dev server, docker-compose, etc.)
   - How to run tests if test config is visible
   - Common gotchas or setup issues visible from the config files
   
3. "env_vars": A JSON array of ALL environment variables mentioned anywhere in the files. For each, include the variable name. If a default value or description is visible, include it as a comment.

Return ONLY valid JSON. Do NOT truncate your response — completeness is critical."""

    from app.utils.llm_retry import retry_llm_call
    
    @retry_llm_call(max_retries=5, initial_delay=2)
    def call_llm(client):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(response_mime_type="application/json")
        )
        import json
        result = json.loads(response.text)
        return {
            "architecture_overview": result.get("architecture_overview", "Analysis failed."),
            "getting_started": result.get("getting_started", "Instructions not found."),
            "env_vars": result.get("env_vars", [])
        }
        
    return call_llm()
