"""Pydantic schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class WorkflowExecutionCreate(BaseModel):
    workflow_name: str
    workflow_type: str
    input_data: dict | None = None
    output_data: dict | None = None
    status: str = "success"
    execution_time_ms: int | None = None
    tokens_used: int = 0
    error_message: str | None = None


class WorkflowExecutionRead(WorkflowExecutionCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
