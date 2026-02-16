from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database.models_db import User
from database.database import get_db
from tools.auth_func import require_permission

admin_router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@admin_router.get("/users", response_model=List[dict])
async def get_all_users(current_user: User = Depends(require_permission("users", "read_all")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить список всех пользователей (требуется разрешение на чтение всех пользователей)
    """

    result = await db.execute(select(User))
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "patronymic": user.patronymic,
            "is_active": user.is_active,
            "is_role": user.is_role
        }
        for user in users
    ]


@admin_router.get("/users/{user_id}", response_model=dict)
async def get_user_by_id(user_id: int, current_user: User = Depends(require_permission("users", "read")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить информацию о конкретном пользователе (требуется разрешение на чтение пользователей)
    """

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "patronymic": user.patronymic,
        "is_active": user.is_active,
        "is_role": user.is_role
    }


@admin_router.put("/users/{user_id}/role")
async def update_user_role(user_id: int, new_role: str, current_user: User = Depends(require_permission("users", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Обновить роль пользователя (требуется разрешение на обновление пользователей)
    """

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Обновляем роль пользователя
    user.is_role = new_role
    await db.commit()

    return {"message": f"Role updated successfully for user {user_id}", "new_role": new_role}


@admin_router.put("/users/{user_id}/activate")
async def activate_user(user_id: int, current_user: User = Depends(require_permission("users", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Активировать пользователя (требуется разрешение на обновление пользователей)
    """

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    await db.commit()

    return {"message": f"User {user_id} activated successfully"}


@admin_router.put("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, current_user: User = Depends(require_permission("users", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Деактивировать пользователя (требуется разрешение на обновление пользователей)
    """

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Не позволяем деактивировать самого себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself"
        )

    user.is_active = False
    await db.commit()

    return {"message": f"User {user_id} deactivated successfully"}


@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(require_permission("users", "delete")), db: AsyncSession = Depends(get_db)):
    
    """
    Удалить пользователя (требуется разрешение на удаление пользователей)
    """
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Не позволяем удалить самого себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )

    await db.delete(user)
    await db.commit()

    return {"message": f"User {user_id} deleted successfully"}