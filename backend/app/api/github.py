from fastapi import APIRouter, Depends, HTTPException
import httpx
from typing import List, Dict, Any
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/repos", response_model=List[Dict[str, Any]])
async def get_user_repos(current_user: User = Depends(get_current_user)):
    """Fetch the user's GitHub repositories using their stored OAuth token."""
    if not current_user.github_access_token:
        raise HTTPException(status_code=401, detail="GitHub access token not found. Please log in again.")
        
    url = "https://api.github.com/user/repos?sort=updated&per_page=30"
    headers = {
        "Authorization": f"Bearer {current_user.github_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch repositories from GitHub")
            
        repos_data = response.json()
        
        # Filter and map to a simpler format to send to frontend
        simplified_repos = []
        for repo in repos_data:
            simplified_repos.append({
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "html_url": repo.get("html_url"),
                "updated_at": repo.get("updated_at"),
                "private": repo.get("private"),
                "language": repo.get("language")
            })
            
        return simplified_repos

from pydantic import BaseModel
from app.services.github_service import GitHubService

class CheckUpdateResponse(BaseModel):
    remote_sha: str | None

@router.get("/check_update", response_model=CheckUpdateResponse)
async def check_update(repo_url: str, current_user: User = Depends(get_current_user)):
    """Check the latest commit SHA of a repository without cloning it."""
    sha = GitHubService.get_remote_commit_sha(repo_url, current_user.github_access_token)
    return CheckUpdateResponse(remote_sha=sha)
