import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_task(client):
    """Тест создания задачи"""
    payload = {"title": "Test Task", "description": "Desc", "priority": "HIGH"}
    response = await client.post("/api/v1/tasks", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "PENDING"
    assert data["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_create_task_default_priority(client):
    """Тест создания задачи с приоритетом по умолчанию"""
    payload = {"title": "Default Priority Task"}
    response = await client.post("/api/v1/tasks", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "MEDIUM"


@pytest.mark.asyncio
async def test_get_tasks_list(client):
    """Тест получения списка задач"""
    # Создаём задачу
    await client.post("/api/v1/tasks", json={"title": "Task 1"})
    
    # Получаем список
    response = await client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_tasks_with_pagination(client):
    """Тест пагинации списка задач"""
    response = await client.get("/api/v1/tasks?skip=0&limit=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_task_by_id(client):
    """Тест получения задачи по ID"""
    # Создаём задачу
    create_response = await client.post("/api/v1/tasks", json={"title": "Get Test"})
    task_id = create_response.json()["id"]
    
    # Получаем по ID
    response = await client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Test"


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """Тест получения несуществующей задачи"""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_task(client):
    """Тест отмены задачи"""
    # Создаём задачу
    create_response = await client.post("/api/v1/tasks", json={"title": "Cancel Test"})
    task_id = create_response.json()["id"]
    
    # Отменяем
    response = await client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_cancel_task_not_found(client):
    """Тест отмены несуществующей задачи"""
    fake_id = str(uuid4())
    response = await client.delete(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_status(client):
    """Тест получения статуса задачи"""
    # Создаём задачу
    create_response = await client.post("/api/v1/tasks", json={"title": "Status Test"})
    task_id = create_response.json()["id"]
    
    # Получаем статус
    response = await client.get(f"/api/v1/tasks/{task_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_create_task_with_all_priorities(client):
    """Тест создания задач с разными приоритетами"""
    for priority in ["LOW", "MEDIUM", "HIGH"]:
        response = await client.post("/api/v1/tasks", json={
            "title": f"Task {priority}",
            "priority": priority
        })
        assert response.status_code == 201
        assert response.json()["priority"] == priority
