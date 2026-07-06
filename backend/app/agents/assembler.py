import json
from .state import OnboardingState
from app.database import AsyncSessionLocal
from app.models.guide import Guide
import uuid

async def assemble_final_guide_async(state: OnboardingState) -> dict:
    job_id = state["job_id"]
    
    # --- Architecture Section ---
    arch_section = state.get("architecture_overview", "")
    if isinstance(arch_section, list):
        arch_section = "\n".join(arch_section)
    elif not isinstance(arch_section, str):
        arch_section = str(arch_section)
    
    # --- Modules Section (rich formatting) ---
    modules = state.get("key_modules", [])
    modules_parts = []
    for m in modules:
        if not isinstance(m, dict):
            continue
        module_name = m.get("module", "Unknown")
        description = m.get("description", "No description available.")
        key_symbols = m.get("key_symbols", [])
        
        entry = f"### 📦 `{module_name}`\n{description}"
        if key_symbols:
            entry += "\n\n**Key symbols:** " + ", ".join([f"`{s}`" for s in key_symbols])
        modules_parts.append(entry)
    
    modules_section = "\n\n---\n\n".join(modules_parts) if modules_parts else "No module data available."
    
    # --- Docs Health Section (rich formatting) ---
    docs = state.get("docs_health", [])
    docs_parts = []
    accurate_count = 0
    stale_count = 0
    unverifiable_count = 0
    
    for d in docs:
        if not isinstance(d, dict):
            continue
        status = d.get("status", "unknown")
        claim = d.get("claim", "")
        evidence = d.get("evidence", "")
        source = d.get("source_file", "")
        
        if status == "accurate":
            icon = "✅"
            accurate_count += 1
        elif status == "stale":
            icon = "⚠️"
            stale_count += 1
        else:
            icon = "❓"
            unverifiable_count += 1
            
        entry = f"{icon} **{claim}**"
        if source:
            entry += f" _(from {source})_"
        entry += f"\n   {evidence}"
        docs_parts.append(entry)
    
    # Summary header
    docs_header = f"**Summary:** {accurate_count} accurate, {stale_count} stale, {unverifiable_count} unverifiable claims found.\n\n"
    docs_section = docs_header + "\n\n".join(docs_parts) if docs_parts else "No documentation analysis available."
    
    # --- Getting Started Section ---
    getting_started = state.get("getting_started", "")
    if isinstance(getting_started, list):
        getting_started = "\n".join(getting_started)
    elif not isinstance(getting_started, str):
        getting_started = str(getting_started)
        
    env_vars = state.get("env_vars", [])
    if isinstance(env_vars, list) and env_vars:
        env_block = "### Required Environment Variables\n\n"
        env_block += "\n".join([f"- `{str(e)}`" for e in env_vars])
        getting_started = env_block + "\n\n### Setup Steps\n\n" + getting_started
        
    share_slug = f"{job_id[:8]}"
    
    async with AsyncSessionLocal() as session:
        guide = Guide(
            id=str(uuid.uuid4()),
            job_id=job_id,
            architecture_section=arch_section,
            modules_section=modules_section,
            docs_health_section=docs_section,
            getting_started_section=getting_started,
            share_slug=share_slug
        )
        session.add(guide)
        await session.commit()
        
    return {"guide_assembled": True}
    
def assemble_final_guide(state: OnboardingState) -> dict:
    # Wrapper for sync graph execution
    import asyncio
    asyncio.run(assemble_final_guide_async(state))
    return {"guide_assembled": True}
