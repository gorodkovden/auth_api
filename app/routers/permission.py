"""
Permissions Management Router.

Endpoints for managing role-based permissions:
- List all permissions
- Create permissions for a role
- Get permissions by role
- Update permissions for a role
- Delete permissions for a role
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models_db import Permissions, User
from tools.schemas import PermissionCreate, PermissionResponse
from database.database import get_db
from tools.auth_func import require_permission

permission_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@permission_router.get("/", response_model=list[PermissionResponse])
async def get_all_permissions(
    current_user: User = Depends(require_permission("permissions", "read_all")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all permission records.
    
    Args:
        current_user: Authenticated user (requires 'read_all' permission for permissions)
        db: Database session
        
    Returns:
        list[PermissionResponse]: List of all permission records
        
    Raises:
        HTTPException: 403 if user lacks 'read_all' permission
    """
    result = await db.execute(select(Permissions))
    permissions = result.scalars().all()

    return [
        {
            "id": perm.id,
            "role_name": perm.role_name,
            "create_users": perm.create_users,
            "read_users": perm.read_users,
            "read_all_users": perm.read_all_users,
            "update_users": perm.update_users,
            "delete_users": perm.delete_users,
            "create_permissions": perm.create_permissions,
            "read_permissions": perm.read_permissions,
            "read_all_permissions": perm.read_all_permissions,
            "update_permissions": perm.update_permissions,
            "delete_permissions": perm.delete_permissions,
            "create_business_elements": perm.create_business_elements,
            "read_business_elements": perm.read_business_elements,
            "read_all_business_elements": perm.read_all_business_elements,
            "update_business_elements": perm.update_business_elements,
            "delete_business_elements": perm.delete_business_elements
        }
        for perm in permissions
    ]


@permission_router.post("/{role_name}", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("permissions", "create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new permission record for a role.
    
    Args:
        permission_data: Permission data including role name and all permission flags
        current_user: Authenticated user (requires 'create' permission for permissions)
        db: Database session
        
    Returns:
        PermissionResponse: Created permission record
        
    Raises:
        HTTPException: 409 if permissions for role already exist
        HTTPException: 403 if user lacks 'create' permission
    """
    # Check if permissions already exist for this role
    result = await db.execute(select(Permissions).filter(Permissions.role_name == permission_data.role_name))
    existing_permission = result.scalar_one_or_none()

    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permissions for role '{permission_data.role_name}' already exist"
        )

    # Create new permission record
    db_permission = Permissions(
        role_name=permission_data.role_name,
        create_users=permission_data.create_users,
        read_users=permission_data.read_users,
        read_all_users=permission_data.read_all_users,
        update_users=permission_data.update_users,
        delete_users=permission_data.delete_users,
        create_permissions=permission_data.create_permissions,
        read_permissions=permission_data.read_permissions,
        read_all_permissions=permission_data.read_all_permissions,
        update_permissions=permission_data.update_permissions,
        delete_permissions=permission_data.delete_permissions,
        create_business_elements=permission_data.create_business_elements,
        read_business_elements=permission_data.read_business_elements,
        read_all_business_elements=permission_data.read_all_business_elements,
        update_business_elements=permission_data.update_business_elements,
        delete_business_elements=permission_data.delete_business_elements
    )

    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)

    return {
        "id": db_permission.id,
        "role_name": db_permission.role_name,
        "create_users": db_permission.create_users,
        "read_users": db_permission.read_users,
        "read_all_users": db_permission.read_all_users,
        "update_users": db_permission.update_users,
        "delete_users": db_permission.delete_users,
        "create_permissions": db_permission.create_permissions,
        "read_permissions": db_permission.read_permissions,
        "read_all_permissions": db_permission.read_all_permissions,
        "update_permissions": db_permission.update_permissions,
        "delete_permissions": db_permission.delete_permissions,
        "create_business_elements": db_permission.create_business_elements,
        "read_business_elements": db_permission.read_business_elements,
        "read_all_business_elements": db_permission.read_all_business_elements,
        "update_business_elements": db_permission.update_business_elements,
        "delete_business_elements": db_permission.delete_business_elements
    }


@permission_router.get("/{role_name}", response_model=PermissionResponse)
async def get_permissions_by_role(
    role_name: str,
    current_user: User = Depends(require_permission("permissions", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get permissions for a specific role.
    
    Args:
        role_name: Name of the role to get permissions for
        current_user: Authenticated user (requires 'read' permission for permissions)
        db: Database session
        
    Returns:
        PermissionResponse: Permission record for the role
        
    Raises:
        HTTPException: 404 if role not found
        HTTPException: 403 if user lacks 'read' permission
    """
    result = await db.execute(select(Permissions).filter(Permissions.role_name == role_name))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions for role '{role_name}' not found"
        )

    return {
        "id": permission.id,
        "role_name": permission.role_name,
        "create_users": permission.create_users,
        "read_users": permission.read_users,
        "read_all_users": permission.read_all_users,
        "update_users": permission.update_users,
        "delete_users": permission.delete_users,
        "create_permissions": permission.create_permissions,
        "read_permissions": permission.read_permissions,
        "read_all_permissions": permission.read_all_permissions,
        "update_permissions": permission.update_permissions,
        "delete_permissions": permission.delete_permissions,
        "create_business_elements": permission.create_business_elements,
        "read_business_elements": permission.read_business_elements,
        "read_all_business_elements": permission.read_all_business_elements,
        "update_business_elements": permission.update_business_elements,
        "delete_business_elements": permission.delete_business_elements
    }


@permission_router.put("/{role_name}", response_model=PermissionResponse)
async def update_permissions_by_role(
    role_name: str,
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("permissions", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update permissions for a specific role.
    
    Args:
        role_name: Name of the role to update
        permission_data: New permission data
        current_user: Authenticated user (requires 'update' permission for permissions)
        db: Database session
        
    Returns:
        PermissionResponse: Updated permission record
        
    Raises:
        HTTPException: 404 if role not found
        HTTPException: 403 if user lacks 'update' permission
    """
    result = await db.execute(select(Permissions).filter(Permissions.role_name == role_name))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions for role '{role_name}' not found"
        )

    # Update all permission fields
    permission.role_name = permission_data.role_name
    permission.create_users = permission_data.create_users
    permission.read_users = permission_data.read_users
    permission.read_all_users = permission_data.read_all_users
    permission.update_users = permission_data.update_users
    permission.delete_users = permission_data.delete_users
    permission.create_permissions = permission_data.create_permissions
    permission.read_permissions = permission_data.read_permissions
    permission.read_all_permissions = permission_data.read_all_permissions
    permission.update_permissions = permission_data.update_permissions
    permission.delete_permissions = permission_data.delete_permissions
    permission.create_business_elements = permission_data.create_business_elements
    permission.read_business_elements = permission_data.read_business_elements
    permission.read_all_business_elements = permission_data.read_all_business_elements
    permission.update_business_elements = permission_data.update_business_elements
    permission.delete_business_elements = permission_data.delete_business_elements

    await db.commit()

    return {
        "id": permission.id,
        "role_name": permission.role_name,
        "create_users": permission.create_users,
        "read_users": permission.read_users,
        "read_all_users": permission.read_all_users,
        "update_users": permission.update_users,
        "delete_users": permission.delete_users,
        "create_permissions": permission.create_permissions,
        "read_permissions": permission.read_permissions,
        "read_all_permissions": permission.read_all_permissions,
        "update_permissions": permission.update_permissions,
        "delete_permissions": permission.delete_permissions,
        "create_business_elements": permission.create_business_elements,
        "read_business_elements": permission.read_business_elements,
        "read_all_business_elements": permission.read_all_business_elements,
        "update_business_elements": permission.update_business_elements,
        "delete_business_elements": permission.delete_business_elements
    }


@permission_router.delete("/{role_name}")
async def delete_permissions_by_role(
    role_name: str,
    current_user: User = Depends(require_permission("permissions", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete permissions for a specific role.
    
    Args:
        role_name: Name of the role to delete permissions for
        current_user: Authenticated user (requires 'delete' permission for permissions)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if role not found
        HTTPException: 403 if user lacks 'delete' permission
    """
    result = await db.execute(select(Permissions).filter(Permissions.role_name == role_name))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions for role '{role_name}' not found"
        )

    await db.delete(permission)
    await db.commit()

    return {"message": f"Permissions for role '{role_name}' deleted successfully"}
