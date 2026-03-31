"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "RepoLens"
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repolens"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant (Vector DB)
    QDRANT_URL: str = "http://localhost:6333"

    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Analysis limits
    MAX_REPO_SIZE_MB: int = 500
    MAX_FILES: int = 10000
    MAX_TOKEN_BUDGET: int = 200000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
