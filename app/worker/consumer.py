import asyncio
import json
import logging
from uuid import UUID
from datetime import datetime
import aio_pika
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session_factory
from app.models.task import Task, TaskStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_task(task_id: UUID):
    async with async_session_factory() as db:

        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task or task.status == TaskStatus.CANCELLED:
            logger.info(f"Task {task_id} is cancelled or not found. Skipping.")
            return


        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        await db.commit()

        try:
            for i in range(5):
                await asyncio.sleep(1)

                await db.refresh(task)
                if task.status == TaskStatus.CANCELLED:
                    logger.info(f"Task {task_id} was cancelled during execution.")
                    return


            task.status = TaskStatus.COMPLETED
            task.result = "Processed successfully"
            task.finished_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Task {task_id} completed.")

        except Exception as e:
 
            task.status = TaskStatus.FAILED
            task.error_info = str(e)
            task.finished_at = datetime.utcnow()
            await db.commit()
            logger.error(f"Task {task_id} failed: {e}")

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):
        try:
            body = json.loads(message.body.decode())
            task_id = UUID(body["task_id"])
            await process_task(task_id)
            await message.ack()
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.nack(requeue=False)

async def run_worker():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=settings.WORKER_PREFETCH_COUNT)
        
        queue = await channel.declare_queue(
            "tasks_queue", 
            durable=True, 
            arguments={"x-max-priority": 10}
        )
        
        logger.info("Worker started. Waiting for messages...")
        await queue.consume(on_message)
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run_worker())
