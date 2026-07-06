from app.schemas.qa import SourceCitation
from app.services.vector_service import VectorService
from app.services.embedding_service import EmbeddingService
from app.utils.named_entity import extract_named_entity
from google import genai
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import json

class QAService:
    @staticmethod
    async def ask_question(session: AsyncSession, guide_id: str, job_id: str, question: str) -> tuple[str, list[SourceCitation]]:
        named_entity = extract_named_entity(question)
        
        retrieved_chunks = []
        if named_entity:
            # Path A - Hybrid/Exact Symbol Lookup
            chunks = await VectorService.get_by_name(session, job_id, named_entity)
            if chunks:
                retrieved_chunks.extend(chunks)
                # Import graph traversal (fetch 1 level of imports)
                for chunk in chunks:
                    imports = chunk.metadata_json.get("imports", [])
                    for imp in imports[:10]:  # Limit to avoid explosion
                        imp_chunks = await VectorService.get_by_name(session, job_id, imp)
                        retrieved_chunks.extend(imp_chunks)
        
        if not retrieved_chunks:
            # Path B - Semantic Search with higher limit
            emb_service = EmbeddingService()
            query_emb = await emb_service.get_embedding(question)
            retrieved_chunks = await VectorService.query_similar(session, job_id, query_emb, limit=10)
            
        # Deduplicate chunks
        seen = set()
        unique_chunks = []
        for c in retrieved_chunks:
            if c.id not in seen:
                seen.add(c.id)
                unique_chunks.append(c)
                
        # Build Context with full code text
        context = ""
        sources = []
        for c in unique_chunks:
            meta = c.metadata_json
            file_path = meta.get("file", "unknown")
            start_line = meta.get("start_line")
            end_line = meta.get("end_line")
            name = meta.get("name", "unnamed")
            chunk_type = meta.get("type", "chunk")
            text = meta.get("text", "")
            
            context += f"=== {file_path} (Lines {start_line}-{end_line}) [{chunk_type}: {name}] ===\n"
            context += f"{text}\n\n"
            
            sources.append(SourceCitation(
                file=file_path,
                start_line=start_line,
                end_line=end_line,
                type=meta.get("type"),
                name=name
            ))
            
        prompt = f"""You are a senior software engineer answering questions about a specific codebase. You have been given relevant code chunks retrieved from the codebase.

=== RESPONSE LENGTH GUIDELINES ===

**Match your answer length to the question complexity:**
- **Simple factual questions** (e.g., "What database does this use?", "Where is the config file?"): Give a **1-3 sentence** direct answer. Do NOT over-explain.
- **How-does-X-work questions**: Give a **medium-length** answer (1-2 short paragraphs) with a step-by-step flow.
- **Deep architectural questions** (e.g., "Explain the entire auth system"): Give a **thorough** multi-paragraph answer with execution tracing.

Always be as concise as the question demands. Never pad your answer.

=== FORMAT GUIDELINES ===

- When referencing code, cite `file_path:line_number`.
- Include short inline code snippets when they add clarity.
- For flow explanations, use numbered steps.
- Use markdown formatting (bold, code blocks, lists) for readability.
- If the context is insufficient, say exactly what's missing.

=== QUESTION ===
{question}

=== CODE CONTEXT ===
{context}

Answer based ONLY on the provided code context. Be specific — reference actual names and file paths."""
        
        from app.utils.llm_retry import retry_llm_call
        
        @retry_llm_call(max_retries=5, initial_delay=2)
        def call_llm(client):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
            
        try:
            answer = call_llm()
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
            
        return answer, sources

