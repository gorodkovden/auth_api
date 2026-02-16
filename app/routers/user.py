from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models_db import User
from tools.auth_func import require_permission
from database.database import get_db

user_router = APIRouter(prefix="/profile", tags=["User Panel"])

@user_router.get("/")
async def get_profile(current_user: User = Depends(require_permission("users", "read")), db: AsyncSession = Depends(get_db)):
    
    """
    User profile information
    """

    result = await db.execute(select(User).filter(User.id == current_user.id))
    user_data = result.scalar_one_or_none()

    if user_data:
        return {
            "id": user_data.id,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "patronymic": user_data.patronymic,
            "email": user_data.email,
            "is_active": user_data.is_active,
            "is_role": user_data.is_role,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )


@user_router.put("/delete")
async def deactivate_account(current_user: User = Depends(require_permission("users", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Soft delete account (требуется разрешение на обновление пользователей)
    """

    if current_user:
        result = await db.execute(select(User).filter(User.id == current_user.id))
        user = result.scalar_one_or_none()

        if user.is_role == "admin":
            return {"message": "Admin cannot be deactivated in this"}

        user.is_active = False
        await db.commit()

        return {"message": "Account deactivated successfully"}
    

@user_router.put("/update/{parameter}")
async def update_profile(parameter: str, value: str, current_user: User = Depends(require_permission("users", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Update profile information
    """

    if current_user:
        result = await db.execute(select(User).filter(User.id == current_user.id))
        user = result.scalar_one_or_none()
        
        if not hasattr(user, parameter):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter '{parameter}' does not exist in User model"
            )
            
        setattr(user, parameter, value)
        await db.commit()

        return {"message": f"{parameter} updated successfully"}
    