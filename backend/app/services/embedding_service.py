import os
import asyncio
from typing import List
from google.genai import types
from app.utils.key_manager import gemini_key_manager

class EmbeddingService:
    def __init__(self):
        pass # Keys managed globally now
            
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        max_retries = 10
        delay = 2
        
        for attempt in range(max_retries):
            client = gemini_key_manager.get_client()
            if not client:
                # Fallback for dev without keys
                return [[0.0] * 768 for _ in texts]
                
            wait_time = gemini_key_manager.get_wait_time(client)
            if wait_time > 0:
                print(f"All keys exhausted. Sleeping for {wait_time:.1f}s...")
                await asyncio.sleep(wait_time + 1)
                
            try:
                # Using gemini-embedding-2 which outputs 768 dims by default
                response = client.models.embed_content(
                    model='gemini-embedding-2',
                    contents=texts,
                    config=types.EmbedContentConfig(output_dimensionality=768)
                )
                return [e.values for e in response.embeddings]
            except Exception as e:
                err_str = str(e)
                if attempt < max_retries - 1:
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        print(f"Embeddings Rate limit hit. Swapping API key... {err_str}")
                        gemini_key_manager.mark_exhausted(client)
                        await asyncio.sleep(0.5)
                    else:
                        print(f"Embedding generic error. Retrying in {delay}s: {err_str}")
                        await asyncio.sleep(delay)
                        delay *= 2
                else:
                    raise RuntimeError(f"Embedding failed after {max_retries} attempts: {e}")

    async def get_embedding(self, text: str) -> List[float]:
        results = await self.get_embeddings([text])
        return results[0]
