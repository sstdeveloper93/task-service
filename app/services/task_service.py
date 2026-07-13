from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate
from app.worker.rabbit import RabbitMQPublisher
from fastapi import HTTPException

class TaskService:
    def __init__(self, db: AsyncSession, publisher: RabbitMQPublisher):
        self.db = db
        self.publisher = publisher

    async def create_task(self, data: TaskCreate) -> Task:
        task = Task(title=data.title, description=data.description, priority=data.priority, status=TaskStatus.PENDING)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        # Отправляем в RabbitMQ
        await self.publisher.publish_task(task.id, task.priority.rabbitmq_priority)
        return task

    async def get_tasks(self, skip: int = 0, limit: int = 20, status: TaskStatus | None = None):
        query = select(Task).order_by(desc(Task.created_at))
        if status:
            query = query.where(Task.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_task(self, task_id: UUID) -> Task:
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def cancel_task(self, task_id: UUID) -> Task:
        task = await self.get_task(task_id)
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel task in {task.status} status")
        
        task.status = TaskStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(task)
        return task
