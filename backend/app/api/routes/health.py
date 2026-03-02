"""Health check endpoint."""
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["health"])

@router.get("/api/v1/health")
async def health():
    s = get_settings()
    return {"status": "healthy", "version": s.app_version, "environment": s.environment}
