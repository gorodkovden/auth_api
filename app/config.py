"""
Application settings and configuration.

Loads environment variables from .env file and provides
type-safe configuration for the entire application.
"""

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        DB_USER: Database username
        DB_PASSWORD: Database password
        DB_HOST: Database host
        DB_PORT: Database port
        DB_NAME: Database name
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        pool_pre_ping: Enable connection health checks
        echo: Enable SQL query logging
        SECRET_KEY: JWT signing secret key
        ALGORITHM: JWT algorithm (default: HS256)
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime in minutes
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime in days
    """

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # Database configuration
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "auth_db")

    # Database connection pool configuration
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True  # Enable connection health check before use
    echo: bool = False  # Enable SQL query logging

    # JWT configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    @property
    def database_url(self) -> str:
        """
        Build PostgreSQL async database URL.
        
        Returns:
            str: Database connection URL in format:
                 postgresql+asyncpg://user:password@host:port/database
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Global settings instance
settings = Settings()
