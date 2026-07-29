import re
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Cognitive Metrics AI Backend"
    API_V1_STR: str = "/api/v1"

    # Default to SQLite for local dev, overridden by Neon PostgreSQL connection string in .env
    DATABASE_URL: str = "sqlite+aiosqlite:///./cognitive_metrics.db"

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            # Trim quotes if user added quotes around connection string in .env
            v = v.strip("'\"")
            
            # Normalize scheme for asyncpg
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Convert libpq 'sslmode' parameter to asyncpg 'ssl' parameter
            if "postgresql+asyncpg://" in v:
                v = re.sub(r'[?&]sslmode=([^&]+)', r'?ssl=\1', v, count=1)
                # Remove extra unsupported libpq query parameters like channel_binding, gssencmode
                v = re.sub(r'&channel_binding=[^&]+', '', v)
                v = re.sub(r'\?channel_binding=[^&]+&?', '?', v)
                v = re.sub(r'&gssencmode=[^&]+', '', v)

        return v


settings = Settings()
