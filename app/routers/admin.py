"""
Admin Panel Router.

Endpoints for user management (requires admin permissions):
- List all users
- Get user by ID
- Update user role
- Activate/deactivate users
- Delete users
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database.models_db import User
from database.database import get_db
from tools.auth_func import require_permission

admin_router = APIRouter(prefix="/admin", tags=["Admin Panel"])


@admin_router.get("/users", response_model=List[dict])
async def get_all_users(
    current_user: User = Depends(require_permission("users", "read_all")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all users.
    
    Args:
        current_user: Authenticated user (requires 'read_all' permission for users)
        db: Database session
        
    Returns:
        List[dict]: List of all users with their details
        
    Raises:
        HTTPException: 403 if user lacks 'read_all' permission
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
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_permission("users", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details by ID.
    
    Args:
        user_id: ID of user to retrieve
        current_user: Authenticated user (requires 'read' permission for users)
        db: Database session
        
    Returns:
        dict: User details
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if user lacks 'read' permission
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
async def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's role.
    
    Args:
        user_id: ID of user to update
        new_role: New role name to assign
        current_user: Authenticated user (requires 'update' permission for users)
        db: Database session
        
    Returns:
        dict: Success message with new role
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if user lacks 'update' permission
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user role
    user.is_role = new_role
    await db.commit()

    return {"message": f"Role updated successfully for user {user_id}", "new_role": new_role}


@admin_router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a user account.
    
    Args:
        user_id: ID of user to activate
        current_user: Authenticated user (requires 'update' permission for users)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if user lacks 'update' permission
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
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user account.
    
    Args:
        user_id: ID of user to deactivate
        current_user: Authenticated user (requires 'update' permission for users)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if trying to deactivate yourself
        HTTPException: 403 if user lacks 'update' permission
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself"
        )

    user.is_active = False
    await db.commit()

    return {"message": f"User {user_id} deactivated successfully"}


@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("users", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user account.
    
    Args:
        user_id: ID of user to delete
        current_user: Authenticated user (requires 'delete' permission for users)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if trying to delete yourself
        HTTPException: 403 if user lacks 'delete' permission
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )

    await db.delete(user)
    await db.commit()

    return {"message": f"User {user_id} deleted successfully"}
