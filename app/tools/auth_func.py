"""
Authentication and Authorization Functions.

This module provides:
- JWT token creation and decoding
- Refresh token management with database storage
- Current user extraction from tokens
- Permission checking for RBAC
- Expired token cleanup
"""

from datetime import datetime, timedelta
import datetime as D
from config import settings
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.future import select
from sqlalchemy import delete
from database.models_db import User, Permissions, RefreshToken
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# HTTP Bearer token security scheme
security = HTTPBearer()


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: ID of the user to create token for
        
    Returns:
        str: Encoded JWT access token
        
    Notes:
        - Token expires after ACCESS_TOKEN_EXPIRE_MINUTES
        - Contains user ID in 'sub' claim
        - Token type is 'access'
    """
    expire = datetime.now(D.timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


async def create_refresh_token(user_id: int, db: AsyncSession) -> str:
    """
    Create a JWT refresh token and store it in the database.
    
    Args:
        user_id: ID of the user to create token for
        db: Database session
        
    Returns:
        str: Encoded JWT refresh token
        
    Notes:
        - Token expires after REFRESH_TOKEN_EXPIRE_DAYS
        - Stored in database for revocation support
        - Contains expiration timestamp in expires_at field
    """
    expire = datetime.now(D.timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expire
    )

    db.add(db_token)
    await db.commit()

    return token


async def cleanup_expired_refresh_tokens(db: AsyncSession) -> int:
    """
    Delete all expired refresh tokens from the database.
    
    Args:
        db: Database session
        
    Returns:
        int: Number of deleted tokens
        
    Notes:
        - Called automatically on login
        - Can be called manually via /authentication/cleanup-tokens
        - Helps maintain database size
    """
    now = datetime.now(D.timezone.utc)
    result = await db.execute(
        delete(RefreshToken).where(RefreshToken.expires_at < now)
    )
    await db.commit()
    return result.rowcount or 0


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        dict | None: Decoded payload if valid, None otherwise
        
    Notes:
        - Returns None on expiration or invalid signature
        - Does not raise exceptions (handled internally)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.PyJWTError:
        # Other decoding errors
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract and validate current user ID from JWT access token.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        int: User ID from token
        
    Raises:
        HTTPException: 401 if token is invalid, expired, or wrong type
        
    Notes:
        - Only accepts 'access' token type
        - Returns user ID as integer
    """
    token = credentials.credentials
    payload = decode_token(token)

    # Check if token is valid and not expired
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
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

    # Return user ID as integer
    return int(user_id)


async def check_permission(
    user_id: int,
    resource: str,
    action: str,
    db: AsyncSession
) -> bool:
    """
    Check if user has permission to perform action on resource.
    
    Args:
        user_id: ID of the user to check
        resource: Resource name ('users', 'permissions', 'business_elements')
        action: Action name ('create', 'read', 'read_all', 'update', 'delete')
        db: Database session
        
    Returns:
        bool: True if permission granted
        
    Raises:
        HTTPException: 404 if user not found, 403 if permission denied
        
    Notes:
        - Admin role bypasses all permission checks
        - Permission attribute format: {action}_{resource}
    """
    # Get user from database
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Admin role has full access
    if user.is_role == "admin":
        return True

    # Get permissions for user's role
    permission_result = await db.execute(
        select(Permissions).filter(Permissions.role_name == user.is_role)
    )
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No permissions defined for role '{user.is_role}'"
        )

    # Build permission attribute name
    permission_attr = f"{action}_{resource}"

    # Check if permission attribute exists
    if not hasattr(Permissions, permission_attr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission attribute '{permission_attr}' not found"
        )

    # Get permission value
    has_permission = getattr(permission, permission_attr, False)

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Role '{user.is_role}' does not have permission to {action} {resource}."
        )

    return True


def require_permission(resource: str, action: str):
    """
    Create a dependency for checking permissions on endpoints.
    
    Args:
        resource: Resource name ('users', 'permissions', 'business_elements')
        action: Action name ('create', 'read', 'read_all', 'update', 'delete')
        
    Returns:
        Callable: Dependency function that checks permission and returns user
        
    Example:
        @app.get("/users")
        async def get_users(current_user: User = Depends(require_permission("users", "read_all"))):
            ...
    """
    async def permission_checker(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # Check permission
        await check_permission(user_id, resource, action, db)
        
        # Get and return user for further use in endpoint
        user_result = await db.execute(select(User).filter(User.id == user_id))
        user = user_result.scalar_one_or_none()
        return user

    return permission_checker
