"""
Authentication Router.

Endpoints for:
- User registration
- Login (access + refresh tokens)
- Token refresh
- Logout (token revocation)
- Expired token cleanup
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import datetime as D

from database.models_db import User, RefreshToken
from tools.schemas import UserRegister, UserLogin, TokenResponse, TokenRefreshRequest
from tools.hash import get_password_hash, verify_password
from tools.auth_func import create_access_token, create_refresh_token, decode_token, cleanup_expired_refresh_tokens
from database.database import get_db

auth_router = APIRouter(prefix="/authentication", tags=["Authentication"])


@auth_router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: Registration data (email, password, name)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 409 if email already exists
        HTTPException: 400 if passwords don't match
    """
    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Validate passwords match
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        patronymic=user_data.patronymic
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return {"message": "User registered successfully"}


@auth_router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and issue tokens.
    
    Args:
        user_data: Login credentials (email, password)
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: 401 if credentials invalid or user inactive
    """
    # Find user by email
    result = await db.execute(select(User).filter(User.email == user_data.email))
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Cleanup expired refresh tokens
    await cleanup_expired_refresh_tokens(db)

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(refresh_request: TokenResponse, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_request: Refresh token
        db: Database session
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: 401 if token invalid, expired, or revoked
        
    Notes:
        - Old refresh token is revoked (deleted)
        - New refresh token is issued
        - Checks both JWT expiration and database expires_at
    """
    # Decode and validate refresh token
    payload = decode_token(refresh_request.refresh_token)

    # Verify token type
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Find token in database
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == refresh_request.refresh_token))
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked or expired"
        )

    # Check expiration in database
    now = datetime.now(D.timezone.utc)
    if token_record.expires_at < now:
        await db.delete(token_record)
        await db.commit()
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired"
        )

    # Revoke old token
    await db.delete(token_record)
    await db.commit()

    # Generate new tokens
    access_token = create_access_token(user_id)
    new_refresh_token = await create_refresh_token(user_id, db)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer"
    }


@auth_router.post("/logout")
async def logout(logout_data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Logout user and revoke refresh token.
    
    Args:
        logout_data: Refresh token to revoke
        db: Database session
        
    Returns:
        dict: Success message
    """
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == logout_data.refresh_token))
    token_record = result.scalar_one_or_none()

    if token_record:
        await db.delete(token_record)
        await db.commit()

    return {"message": "Successfully logged out"}


@auth_router.post("/cleanup-tokens")
async def cleanup_tokens(db: AsyncSession = Depends(get_db)):
    """
    Clean up expired refresh tokens from database.
    
    Args:
        db: Database session
        
    Returns:
        dict: Number of deleted tokens
        
    Notes:
        - Can be called manually for maintenance
        - Also called automatically on login
    """
    deleted_count = await cleanup_expired_refresh_tokens(db)
    return {"message": "Expired tokens cleaned up", "deleted_count": deleted_count}
