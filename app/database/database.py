
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_pre_ping=settings.pool_pre_ping,
    echo=settings.echo
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting a database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Автокоммит при успешном выполнении
        except Exception:
            await session.rollback()  # Откат при ошибке
            raise
        finally:
            await session.close()  # Закрытие сессии

async def init_db():
    """
    Инициализация базы данных (создание всех таблиц).
    Вызывается при запуске приложения.
    """
    async with engine.begin() as conn:
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)

async def dispose_db():
    """
    Очистка ресурсов БД (закрытие пула соединений).
    Вызывается при завершении приложения.
    """
    await engine.dispose()