from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth_router
from routers.admin import admin_router
from routers.user import user_router
from routers.permission import permission_router
from routers.busines_elements import busines_elements_router
from database.database import init_db, dispose_db
from config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске и очистка при завершении"""
    # Инициализация БД при запуске
    await init_db()
    print(f"База данных инициализирована: {settings.database_url}")
    
    yield  # Приложение работает
    
    # Очистка ресурсов при завершении
    await dispose_db()
    print("Ресурсы базы данных освобождены")

# Создаем экземпляр приложения FastAPI
app = FastAPI(
    title="Authentication API",
    description="API для аутентификации пользователей",
    version="1.0.0",
    lifespan=lifespan
)
"""
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
"""
# Подключаем роутеры
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(permission_router)
app.include_router(busines_elements_router)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Authentication API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )