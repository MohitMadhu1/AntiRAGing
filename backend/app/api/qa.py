from fastapi import APIRouter, Depends
from app.schemas.qa import QAAsk, QAResponse
from app.services.qa_service import QAService
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.guide import Guide
from app.models.user import User
from app.utils.security import get_current_user
from sqlalchemy import select

router = APIRouter()

@router.post("/ask", response_model=QAResponse)
async def ask_question(qa_in: QAAsk, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify guide exists and get job_id
    stmt = select(Guide).where(Guide.id == qa_in.guide_id)
    result = await db.execute(stmt)
    guide = result.scalar_one_or_none()
    
    if not guide:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Guide not found")
        
    answer, sources = await QAService.ask_question(db, guide.id, guide.job_id, qa_in.question)
    
    return QAResponse(answer=answer, sources=sources)
