"""
Функции аутентификации
"""

from datetime import datetime, timedelta
import datetime as D
from config import settings
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.future import select
from database.models_db import User, Permissions, RefreshToken
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()


def create_access_token(user_id):
    expire = datetime.now(D.timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id), 
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


async def create_refresh_token(user_id: int, db: AsyncSession) -> str:
    expire = datetime.now(D.timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id), 
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    db_token = RefreshToken(
        user_id=user_id,
        token=token
    )

    db.add(db_token)
    await db.commit()

    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Токен истек
        return None
    except jwt.PyJWTError:
        # Другие ошибки при декодировании токена
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    # Проверяем, что токен действителен и не просрочен
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем тип токена
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Возвращаем ID пользователя как целое число
    return int(user_id)


async def check_permission(user_id: int, resource: str, action: str, db: AsyncSession):
    """
    Проверяет права доступа пользователя к ресурсу и действию
    
    Args:
        user_id: ID пользователя
        resource: Название ресурса (например, 'users', 'permissions', 'busines_elements')
        action: Действие ('create', 'read', 'read_all', 'update', 'delete')
        db: Сессия базы данных
    
    Returns:
        bool: True если разрешено, иначе вызывает HTTPException
    """
    # Получаем пользователя
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Если пользователь администратор, разрешаем всё
    if user.is_role == "admin":
        return True
    
    # Получаем права доступа для роли пользователя
    permission_result = await db.execute(
        select(Permissions).filter(Permissions.role_name == user.is_role)
    )
    permission = permission_result.scalar_one_or_none()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No permissions defined for role '{user.is_role}'"
        )
    
    # Формируем имя атрибута для проверки разрешения
    permission_attr = f"{action}_{resource}"
    
    # Проверяем наличие атрибута в модели Permissions
    if not hasattr(Permissions, permission_attr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission attribute '{permission_attr}' not found"
        )
    
    # Получаем значение разрешения
    has_permission = getattr(permission, permission_attr, False)
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Role '{user.is_role}' does not have permission to {action} {resource}."
        )
    
    return True


def require_permission(resource: str, action: str):
    """
    Зависимость для проверки прав доступа
    
    Args:
        resource: Название ресурса (например, 'users', 'permissions', 'busines_elements')
        action: Действие ('create', 'read', 'read_all', 'update', 'delete')
    """
    async def permission_checker(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        await check_permission(user_id, resource, action, db)
        # Также возвращаем пользователя для дальнейшего использования
        user_result = await db.execute(select(User).filter(User.id == user_id))
        user = user_result.scalar_one_or_none()
        return user
    
    return permission_checker
