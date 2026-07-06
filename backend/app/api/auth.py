from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.config import settings
from app.utils.security import create_access_token
import uuid

router = APIRouter()

@router.get("/github/login")
async def github_login():
    if not settings.github_client_id:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured")
        
    # Redirect to GitHub consent screen
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.github_client_id}&scope=repo"
    return RedirectResponse(url=github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str, db: AsyncSession = Depends(get_db)):
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(status_code=500, detail="GitHub credentials not configured")
        
    # 1. Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": settings.github_client_id,
        "client_secret": settings.github_client_secret,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, json=payload, headers=headers)
        token_data = token_resp.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description", "OAuth failed"))
            
        access_token = token_data.get("access_token")
        
        # 2. Fetch user profile from GitHub
        user_url = "https://api.github.com/user"
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_resp = await client.get(user_url, headers=user_headers)
        user_profile = user_resp.json()
        
        github_id = str(user_profile.get("id"))
        email = user_profile.get("email")
        
        if not github_id:
            raise HTTPException(status_code=400, detail="Failed to fetch GitHub profile")
            
    # 3. Create or update User in DB
    stmt = select(User).where(User.github_id == github_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        # Update token if changed
        user.github_access_token = access_token
    else:
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            github_id=github_id,
            github_access_token=access_token
        )
        db.add(user)
        
    await db.commit()
    await db.refresh(user)
    
    # 4. Generate JWT
    jwt_token = create_access_token(data={"sub": user.id})
    
    # 5. Redirect back to frontend dashboard with token in URL (or set cookie)
    # For MVP, we will pass it in the query string to the frontend
    # Update this URL to match your Next.js local port
    frontend_url = "http://localhost:3000/dashboard"
    return RedirectResponse(url=f"{frontend_url}?token={jwt_token}")

