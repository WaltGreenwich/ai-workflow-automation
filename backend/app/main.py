"""
AI Workflow Automation Hub - FastAPI Application Entry Point
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes.health import router as health_router
from app.api.routes.n8n_webhooks import router as n8n_router
from app.api.routes.workflows import router as workflow_router
from app.api.routes.analytics import router as analytics_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

settings = get_settings()

if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered B2B process automation platform combining n8n + LangChain",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(n8n_router)
app.include_router(workflow_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} v{settings.app_version}",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
