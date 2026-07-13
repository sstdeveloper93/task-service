from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusResponse
from app.models.task import TaskStatus
from app.worker.rabbit import get_rabbit_publisher
from app.worker.rabbit import RabbitMQPublisher
from typing import List

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

def get_task_service(
    db: AsyncSession = Depends(get_db),
    publisher: RabbitMQPublisher = Depends(get_rabbit_publisher)
) -> TaskService:
    return TaskService(db, publisher)

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, service: TaskService = Depends(get_task_service)):
    return await service.create_task(data)

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = None,
    service: TaskService = Depends(get_task_service)
):
    return await service.get_tasks(skip, limit, status)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    from uuid import UUID
    return await service.get_task(UUID(task_id))

@router.delete("/{task_id}", response_model=TaskResponse)
async def cancel_task(task_id: str, service: TaskService = Depends(get_task_service)):
    from uuid import UUID
    return await service.cancel_task(UUID(task_id))

@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, service: TaskService = Depends(get_task_service)):
    from uuid import UUID
    task = await service.get_task(UUID(task_id))
    return TaskStatusResponse(id=task.id, status=task.status)
