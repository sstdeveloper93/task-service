from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: Optional[str]
    error_info: Optional[str]

class TaskStatusResponse(BaseModel):
    id: UUID
    status: TaskStatus
