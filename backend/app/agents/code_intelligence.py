import asyncio
from typing import List, Dict, Any
from .state import OnboardingState
from google import genai
from app.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.database import AsyncSessionLocal

async def query_chroma_async(job_id: str, query: str) -> str:
    """Wrapper to get embeddings and search pgvector, returning full chunk text."""
    emb_service = EmbeddingService()
    query_emb = await emb_service.get_embedding(query)
    
    context = ""
    async with AsyncSessionLocal() as session:
        chunks = await VectorService.query_similar(session, job_id, query_emb, limit=10)
        for c in chunks:
            meta = c.metadata_json
            file_path = meta.get("file", "unknown")
            name = meta.get("name", "unnamed")
            chunk_type = meta.get("type", "chunk")
            start_line = meta.get("start_line", "?")
            end_line = meta.get("end_line", "?")
            text = meta.get("text", "")
            
            context += f"--- {file_path} (Lines {start_line}-{end_line}) [{chunk_type}: {name}] ---\n"
            context += f"{text}\n\n"
    return context

def run_code_intelligence_agent(state: OnboardingState) -> dict:
    job_id = state["job_id"]
    return {"key_modules": []}

async def run_code_intelligence_agent_async(state: OnboardingState) -> dict:
    job_id = state["job_id"]
    
    queries = [
        "entry points main server application startup initialization",
        "authentication login JWT OAuth token session user credentials",
        "database models schema ORM SQLAlchemy Mongoose Prisma migrations",
        "background jobs workers Celery task queue async processing",
        "API routes controllers endpoints handlers HTTP request response",
        "configuration settings environment variables config",
        "middleware error handling validation logging",
        "data validation schemas serialization Pydantic marshmallow",
        "external services integrations third-party API clients",
        "testing test suite fixtures mocks assertions"
    ]
    
    context = ""
    for q in queries:
        context += f"=== Semantic Query: \"{q}\" ===\n"
        result = await query_chroma_async(job_id, q)
        if result.strip():
            context += result
        else:
            context += "(No relevant chunks found for this query)\n\n"
        
    prompt = f"""You are a principal engineer performing a thorough code analysis for a developer onboarding guide. You have been given code excerpts retrieved via semantic search across the entire codebase.

Analyze ALL of the following code excerpts carefully:

{context}

Your task: Identify and describe EVERY significant module, package, or functional area in this codebase.

Output a JSON array of objects. For EACH module, provide:

1. "module": The file path or directory (e.g., "app/auth/" or "src/models/user.ts")
2. "description": A DETAILED description (3-5 sentences) explaining:
   - What this module/area is responsible for
   - The key classes, functions, or exports it contains (name them specifically)
   - How it connects to or depends on other parts of the system
   - Any notable patterns, design decisions, or technologies used within it
3. "key_symbols": A list of the most important function/class names found in this module (e.g., ["login_user", "create_jwt", "UserModel"])

Be comprehensive — identify at least 5-10 modules if the codebase is non-trivial. Group related files into logical modules rather than listing every single file.

Return ONLY a valid JSON array. Do NOT truncate — completeness is critical."""
    
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
        return {"key_modules": result if isinstance(result, list) else []}
        
    return call_llm()
