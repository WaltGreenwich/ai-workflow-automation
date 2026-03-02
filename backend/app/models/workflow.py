"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.database import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_name = Column(String(255), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    status = Column(String(50), default="success")
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 4), default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    template_type = Column(String(50))
    content = Column(Text, nullable=False)
    variables = Column(JSONB)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowConfig(Base):
    __tablename__ = "workflow_configs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    n8n_workflow_id = Column(String(255))
    enabled = Column(Boolean, default=True)
    config = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
