from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    github_app_id: str
    github_private_key: str
    github_webhook_secret: str
    redis_url: str = "redis://localhost:6379/0"
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

settings = Settings()