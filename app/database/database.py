"""
Database configuration and session management.

This module handles:
- Async engine creation with connection pooling
- Session factory for database operations
- Database initialization and cleanup
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from config import settings

# Base class for declarative models
Base = declarative_base()

# Create async engine with connection pool configuration
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_pre_ping=settings.pool_pre_ping,
    echo=settings.echo
)

# Session factory for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting a database session.
    
    Yields:
        AsyncSession: Database session for request handling
        
    Notes:
        - Automatically commits on success
        - Rolls back on exception
        - Always closes session in finally block
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()  # Close session


async def init_db():
    """
    Initialize database by creating all tables.
    
    Called during application startup via lifespan context manager.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db():
    """
    Dispose database engine and close all connections.
    
    Called during application shutdown via lifespan context manager.
    """
    await engine.dispose()
