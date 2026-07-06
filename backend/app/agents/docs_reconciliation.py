import os
import json
from .state import OnboardingState
from google import genai
from app.config import settings

def run_docs_agent(state: OnboardingState) -> dict:
    repo_path = state["repo_path"]
    
    # Read all documentation files
    doc_content = ""
    doc_files = ["README.md", "CONTRIBUTING.md", "ARCHITECTURE.md", "docs/README.md", 
                 "CHANGELOG.md", "SETUP.md", "INSTALL.md"]
    
    for doc_file in doc_files:
        doc_path = os.path.join(repo_path, doc_file)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()[:6000]
                doc_content += f"=== {doc_file} ===\n{content}\n\n"
            except Exception:
                pass
    
    # Also check for docs/ directory
    docs_dir = os.path.join(repo_path, "docs")
    if os.path.isdir(docs_dir):
        for f in os.listdir(docs_dir)[:10]:  # Limit to first 10 docs
            if f.endswith((".md", ".mdx", ".txt", ".rst")):
                path = os.path.join(docs_dir, f)
                rel_path = os.path.relpath(path, repo_path)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        doc_content += f"=== {rel_path} ===\n{fh.read()[:3000]}\n\n"
                except Exception:
                    pass
                
    if not doc_content:
        return {"docs_health": [{"claim": "Documentation exists", "status": "stale", "evidence": "No README.md or documentation files found in the repository. This is a significant gap — new developers have no written starting point."}]}
    
    # Build a rich reference of what the code actually does
    arch_overview = state.get("architecture_overview", "Unknown")
    key_modules = state.get("key_modules", [])
    
    modules_summary = ""
    for m in key_modules:
        if isinstance(m, dict):
            modules_summary += f"- {m.get('module', 'Unknown')}: {m.get('description', '')}\n"
    
    prompt = f"""You are a documentation quality auditor. Your job is to compare what the documentation CLAIMS against what the code ACTUALLY does.

=== GROUND TRUTH: What the code actually does (from automated code analysis) ===

Architecture Overview:
{arch_overview}

Key Modules Found in Code:
{modules_summary if modules_summary else "No module data available."}

=== DOCUMENTATION TO AUDIT ===

{doc_content}

=== YOUR TASK ===

Extract EVERY verifiable factual claim from the documentation. A "claim" is any statement about:
- What technology, database, or framework is used
- How to install or run the project  
- What features exist
- What directories or files contain what functionality
- API endpoints or interfaces described
- Authentication/authorization mechanisms described

For EACH claim, verify it against the ground truth code analysis and classify it:
- "accurate" — the claim matches what the code actually does
- "stale" — the claim contradicts or doesn't match the actual code
- "unverifiable" — cannot be confirmed or denied from available data

Output a JSON array of objects with keys:
1. "claim": The specific claim from the documentation (quote it)
2. "status": "accurate", "stale", or "unverifiable"  
3. "evidence": A DETAILED explanation of why — reference specific files, modules, or configuration that confirms or contradicts the claim
4. "source_file": Which documentation file the claim came from

Be thorough — extract at least 5-10 claims if the documentation is substantial. Flag EVERY contradiction you find.

Return ONLY a valid JSON array."""
    
    from app.utils.llm_retry import retry_llm_call
    
    @retry_llm_call(max_retries=5, initial_delay=2)
    def call_llm(client):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(response_mime_type="application/json")
        )
        result = json.loads(response.text)
        return {"docs_health": result if isinstance(result, list) else []}
        
    return call_llm()
