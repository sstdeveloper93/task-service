from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tasks"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    WORKER_PREFETCH_COUNT: int = 10

settings = Settings()
