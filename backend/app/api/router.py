from fastapi import APIRouter
from . import jobs, guides, qa, auth, github

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(guides.router, prefix="/guides", tags=["guides"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
