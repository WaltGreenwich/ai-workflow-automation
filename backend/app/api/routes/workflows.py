"""Workflow management endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

MOCK_WORKFLOWS = [
    {"id": "wf-001", "name": "Lead Qualification Pipeline",
     "description": "AI-powered lead scoring and routing",
     "status": "active", "lastRun": "2 min ago", "successRate": 97.5, "avgTime": 1240, "executions": 342},
    {"id": "wf-002", "name": "Email Intelligence & Routing",
     "description": "Auto-classify and route incoming emails",
     "status": "active", "lastRun": "5 min ago", "successRate": 99.1, "avgTime": 890, "executions": 1205},
    {"id": "wf-003", "name": "Content Generation Pipeline",
     "description": "Daily AI content creation and publishing",
     "status": "active", "lastRun": "4 hours ago", "successRate": 95.2, "avgTime": 4500, "executions": 28},
    {"id": "wf-004", "name": "Document Processing",
     "description": "Automated PDF analysis and data extraction",
     "status": "active", "lastRun": "1 hour ago", "successRate": 98.8, "avgTime": 2100, "executions": 76},
]

@router.get("")
async def list_workflows():
    return {"workflows": MOCK_WORKFLOWS, "total": len(MOCK_WORKFLOWS)}
