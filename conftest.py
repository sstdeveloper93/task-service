import asyncio
import sys
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.worker.rabbit import get_rabbit_publisher
from app.core.config import settings

# Windows fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Мокаем RabbitMQ глобально
import app.worker.rabbit as rabbit_module
rabbit_module.publisher_instance = AsyncMock()


@pytest_asyncio.fixture
async def client():
    """Каждый тест получает свою изолированную сессию"""
    # Создаём отдельный engine для каждого теста
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаём сессию
    async with session_factory() as session:
        async def override_get_db():
            yield session
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_rabbit_publisher] = lambda: AsyncMock()
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        
        app.dependency_overrides.clear()
    
    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
