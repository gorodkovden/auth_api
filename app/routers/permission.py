from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models_db import Permissions, User
from tools.shemas import PermissionCreate, PermissionResponse
from database.database import get_db
from tools.auth_func import require_permission

permission_router = APIRouter(prefix="/permissions", tags=["Permissions"])

@permission_router.get("/", response_model=list[PermissionResponse])
async def get_all_permissions(current_user: User = Depends(require_permission("permissions", "read_all")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить все права доступа (требуется разрешение на чтение всех прав)
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
            "create_busines_elements": perm.create_busines_elements,
            "read_busines_elements": perm.read_busines_elements,
            "read_all_busines_elements": perm.read_all_busines_elements,
            "update_busines_elements": perm.update_busines_elements,
            "delete_busines_elements": perm.delete_busines_elements

        }
        for perm in permissions
    ]


@permission_router.post("/{role_name}", response_model=PermissionResponse)
async def create_permission(permission_data: PermissionCreate, current_user: User = Depends(require_permission("permissions", "create")), db: AsyncSession = Depends(get_db)):
    
    """
    Создать новую запись прав доступа (требуется разрешение на создание прав)
    """

    result = await db.execute(select(Permissions).filter(Permissions.role_name == permission_data.role_name))
    existing_permission = result.scalar_one_or_none()

    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permissions for role '{permission_data.role_name}' already exist"
        )

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

        create_busines_elements=permission_data.create_busines_elements,
        read_busines_elements=permission_data.read_busines_elements,
        read_all_busines_elements=permission_data.read_all_busines_elements,
        update_busines_elements=permission_data.update_busines_elements,
        delete_busines_elements=permission_data.delete_busines_elements
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

        "create_busines_elements": db_permission.create_busines_elements,
        "read_busines_elements": db_permission.read_busines_elements,
        "read_all_busines_elements": db_permission.read_all_busines_elements,
        "update_busines_elements": db_permission.update_busines_elements,
        "delete_busines_elements": db_permission.delete_busines_elements
    }


@permission_router.get("/{role_name}", response_model=PermissionResponse)
async def get_permissions_by_role(role_name: str, current_user: User = Depends(require_permission("permissions", "read")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить права доступа для определенной роли (требуется разрешение на чтение прав)
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
        
        "create_busines_elements": permission.create_busines_elements,
        "read_busines_elements": permission.read_busines_elements,
        "read_all_busines_elements": permission.read_all_busines_elements,
        "update_busines_elements": permission.update_busines_elements,
        "delete_busines_elements": permission.delete_busines_elements
    }


@permission_router.put("/{role_name}", response_model=PermissionResponse)
async def update_permissions_by_role(
    role_name: str,
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("permissions", "update")),
    db: AsyncSession = Depends(get_db)
):
    
    """
    Обновить права доступа для определенной роли (требуется разрешение на обновление прав)
    """

    result = await db.execute(select(Permissions).filter(Permissions.role_name == role_name))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions for role '{role_name}' not found"
        )

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
    
    permission.create_busines_elements = permission_data.create_busines_elements
    permission.read_busines_elements = permission_data.read_busines_elements
    permission.read_all_busines_elements = permission_data.read_all_busines_elements
    permission.update_busines_elements = permission_data.update_busines_elements
    permission.delete_busines_elements = permission_data.delete_busines_elements

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
        
        "create_busines_elements": permission.create_busines_elements,
        "read_busines_elements": permission.read_busines_elements,
        "read_all_busines_elements": permission.read_all_busines_elements,
        "update_busines_elements": permission.update_busines_elements,
        "delete_busines_elements": permission.delete_busines_elements
    }


@permission_router.delete("/{role_name}")
async def delete_permissions_by_role(role_name: str, current_user: User = Depends(require_permission("permissions", "delete")), db: AsyncSession = Depends(get_db)):
    
    """
    Удалить права доступа для определенной роли (требуется разрешение на удаление прав)
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

