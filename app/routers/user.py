"""
User Profile Router.

Endpoints for user self-management:
- Get own profile
- Deactivate own account (soft delete)
- Update own profile fields
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models_db import User
from tools.auth_func import require_permission
from database.database import get_db

user_router = APIRouter(prefix="/profile", tags=["User Panel"])


@user_router.get("/")
async def get_profile(
    current_user: User = Depends(require_permission("users", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile information.
    
    Args:
        current_user: Authenticated user (requires 'read' permission for users)
        db: Database session
        
    Returns:
        dict: User profile data
        
    Raises:
        HTTPException: 404 if user not found
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
async def deactivate_account(
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate own account (soft delete).
    
    Args:
        current_user: Authenticated user (requires 'update' permission for users)
        db: Database session
        
    Returns:
        dict: Success message or error for admin users
        
    Raises:
        HTTPException: 403 if user lacks 'update' permission
        
    Notes:
        - Admin accounts cannot be deactivated
        - Sets is_active to False
    """
    if current_user:
        result = await db.execute(select(User).filter(User.id == current_user.id))
        user = result.scalar_one_or_none()

        # Prevent admin deactivation
        if user.is_role == "admin":
            return {"message": "Admin cannot be deactivated"}

        user.is_active = False
        await db.commit()

        return {"message": "Account deactivated successfully"}


@user_router.put("/update/{parameter}")
async def update_profile(
    parameter: str,
    value: str,
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile field.
    
    Args:
        parameter: Field name to update (e.g., 'first_name', 'last_name')
        value: New value for the field
        current_user: Authenticated user (requires 'update' permission for users)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 400 if parameter doesn't exist
        HTTPException: 403 if user lacks 'update' permission
        
    Notes:
        - Only updates string fields
        - Does not validate field values
    """
    if current_user:
        result = await db.execute(select(User).filter(User.id == current_user.id))
        user = result.scalar_one_or_none()

        # Check if parameter exists
        if not hasattr(user, parameter):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter '{parameter}' does not exist in User model"
            )

        # Update field
        setattr(user, parameter, value)
        await db.commit()

        return {"message": f"{parameter} updated successfully"}
