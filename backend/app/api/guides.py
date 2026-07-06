from fastapi import APIRouter, Depends, HTTPException
from app.schemas.guide import GuideResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.guide import Guide

router = APIRouter()

@router.get("/{guide_id}", response_model=GuideResponse)
async def get_guide(guide_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Guide).where(Guide.id == guide_id)
    result = await db.execute(stmt)
    guide = result.scalar_one_or_none()
    if not guide:
        # Check by share_slug as well
        stmt = select(Guide).where(Guide.share_slug == guide_id)
        result = await db.execute(stmt)
        guide = result.scalar_one_or_none()
        if not guide:
            raise HTTPException(status_code=404, detail="Guide not found")
            
    return guide

from app.models.job import Job
from app.models.user import User
from app.utils.security import get_current_user
from sqlalchemy import desc

from sqlalchemy.orm import selectinload

@router.get("/", response_model=list[GuideResponse])
async def get_guides(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Guide).join(Job).where(Job.user_id == current_user.id).order_by(desc(Guide.created_at)).options(selectinload(Guide.job)).limit(20)
    result = await db.execute(stmt)
    guides = result.scalars().all()
    return guides
