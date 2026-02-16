"""
Authentication API - Main Application Entry Point.

This FastAPI application provides:
- User authentication (register, login, refresh, logout)
- Role-based access control (RBAC)
- User management (admin panel)
- Business elements management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth_router
from routers.admin import admin_router
from routers.user import user_router
from routers.permission import permission_router
from routers.business_elements import business_elements_router
from database.database import init_db, dispose_db
from config import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles:
    - Database initialization on startup
    - Resource cleanup on shutdown
    """
    # Initialize database on startup
    await init_db()
    print(f"Database initialized: {settings.database_url}")

    yield  # Application runs here

    # Cleanup resources on shutdown
    await dispose_db()
    print("Database resources disposed")


# Create FastAPI application instance
app = FastAPI(
    title="Authentication API",
    description="REST API for user authentication and role-based access control",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Note: In production, specify exact allowed origins instead of "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(permission_router)
app.include_router(business_elements_router)


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    
    Returns:
        dict: API status information
    """
    return {"message": "Authentication API", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
