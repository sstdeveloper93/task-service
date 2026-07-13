from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as tasks_router
from app.worker.rabbit import init_rabbitmq, close_rabbitmq

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_rabbitmq()
    yield

    await close_rabbitmq()

app = FastAPI(
    title="Task Management Service",
    description="Async task processing with RabbitMQ and FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(tasks_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
