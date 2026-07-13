## 🚀 Быстрый старт

### Запуск проекта в Docker

```powershell
# Запустить все сервисы (API, Worker, PostgreSQL, RabbitMQ)
docker compose up -d

# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (очистить БД)
docker compose down -v

# Пересобрать образы после изменений в коде
docker compose up -d --build

# Посмотреть логи всех сервисов
docker compose logs -f

# Посмотреть логи конкретного сервиса
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f postgres
docker compose logs -f rabbitmq

# Проверить статус контейнеров
docker compose ps

# Перезапустить конкретный сервис
docker compose restart api
docker compose restart worker
```

### Локальный запуск (без Docker)

```powershell
# Активировать виртуальное окружение
.\venv\Scripts\activate

# Запустить API сервер
uvicorn app.main:app --reload

# Запустить worker (в отдельном окне)
python -m app.worker.consumer
```

---

## 🧪 Тестирование

```powershell
# Запустить все тесты
python -m pytest app/tests/test_api.py -v

# Запустить тесты с подробным выводом
python -m pytest app/tests/test_api.py -vv

# Запустить конкретный тест
python -m pytest app/tests/test_api.py::test_create_task -v

# Запустить тесты с покрытием кода (если установлен pytest-cov)
python -m pytest --cov=app --cov-report=html

# Открыть отчёт о покрытии
start htmlcov/index.html
```

---

## 🗄️ Работа с базой данных

### Миграции (Alembic)

```powershell
# Создать новую миграцию автоматически (на основе изменений моделей)
alembic revision --autogenerate -m "описание изменений"

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все миграции
alembic downgrade base

# Посмотреть историю миграций
alembic history

# Посмотреть текущую миграцию
alembic current

# Откатить до конкретной миграции
alembic downgrade <revision_id>
```

### Прямое подключение к PostgreSQL

```powershell
# Подключиться к БД через psql (локально)
& "D:\Soft\PostgreSQL\bin\psql.exe" -U postgres -h 127.0.0.1 -d tasks

# Подключиться к БД в Docker
docker exec -it task-service-git-postgres-1 psql -U postgres -d tasks

# Полезные SQL команды внутри psql:
# \dt                    - показать все таблицы
# \d tasks               - показать структуру таблицы tasks
# SELECT * FROM tasks;   - посмотреть все задачи
# \q                     - выйти из psql
```

---

## 📡 Работа с RabbitMQ

```powershell
# Открыть веб-интерфейс RabbitMQ
start http://127.0.0.1:15672
# Логин: guest, Пароль: guest

# Проверить очереди через CLI (в Docker)
docker exec -it task-service-git-rabbitmq-1 rabbitmqctl list_queues

# Проверить соединения
docker exec -it task-service-git-rabbitmq-1 rabbitmqctl list_connections
```

---

## 🌐 API Endpoints

### Swagger UI (интерактивная документация)

```powershell
start http://127.0.0.1:8000/docs
```

### Альтернативная документация (ReDoc)

```powershell
start http://127.0.0.1:8000/redoc
```

### Проверка здоровья API

```powershell
# Через curl
curl http://127.0.0.1:8000/docs

# Через PowerShell
Invoke-WebRequest -Uri http://127.0.0.1:8000/docs
```

---

## 🛠️ Полезные утилиты

```powershell
# Проверить, какие порты заняты
netstat -ano | findstr "5432"  # PostgreSQL
netstat -ano | findstr "5672"  # RabbitMQ AMQP
netstat -ano | findstr "15672" # RabbitMQ UI
netstat -ano | findstr "8000"  # FastAPI

# Остановить локальный RabbitMQ (если мешает Docker)
net stop RabbitMQ

# Очистить __pycache__
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force

# Обновить зависимости
pip install -r requirements.txt --upgrade
```
