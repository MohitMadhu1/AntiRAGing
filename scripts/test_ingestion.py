import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api"
REPO_URL = "https://github.com/fastapi/fastapi" # Try a relatively small or famous repo for test

async def test_ingestion():
    print(f"Submitting repo {REPO_URL} for ingestion...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/jobs/", json={"repo_url": REPO_URL})
        
        if response.status_code != 200:
            print("Failed to create job:", response.text)
            return
            
        job = response.json()
        job_id = job["id"]
        print(f"Job created successfully: {job_id}")
        
        print("\nListening for SSE progress...")
        try:
            # We use stream to read SSE events
            async with client.stream('GET', f"{BASE_URL}/jobs/{job_id}/progress") as r:
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        print(f"[{data.get('agent')}] {data.get('status')} - {data.get('details', '')}")
                        
                        if data.get("status") in ["Complete", "Error", "failed"]:
                            print("\nJob finished.")
                            break
        except httpx.ReadTimeout:
            print("Timeout reading SSE stream.")
            
        print("\nFetching generated guide...")
        guide_resp = await client.get(f"{BASE_URL}/guides/{job_id[:8]}")
        if guide_resp.status_code == 200:
            guide = guide_resp.json()
            print("Guide successfully retrieved!")
            print("Architecture Section preview:")
            print(guide.get("architecture_section")[:200] + "...")
        else:
            print("Failed to get guide:", guide_resp.text)

if __name__ == "__main__":
    asyncio.run(test_ingestion())
