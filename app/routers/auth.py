from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models_db import User, RefreshToken
from tools.shemas import UserRegister, UserLogin, TokenResponse, TokenRefreshRequest
from tools.hash import get_password_hash, verify_password
from tools.auth_func import create_access_token, create_refresh_token, decode_token
from database.database import get_db

auth_router = APIRouter(prefix="/authentication", tags=["Authentication"])

@auth_router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    
    """
    Register a new user
    """

    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
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
    Login user
    """

    # Находим пользователя по email
    result = await db.execute(select(User).filter(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    # Проверяем, существует ли пользователь и правильный ли пароль
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Проверяем, активен ли пользователь
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Создаем токены для вошедшего пользователя
    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: TokenResponse, db: AsyncSession = Depends(get_db)):
    
    """
    Generation refresh token
    Returns new access and refresh tokens
    Old refresh token will be revoked
    """

    # Декодируем refresh токен
    payload = decode_token(refresh_request.refresh_token)
    
    # Проверяем, что токен действителен и является refresh токеном
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
    
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == refresh_request.refresh_token))

    token_record = result.scalar_one_or_none()
    if not token_record:
        raise HTTPException(
            status_code=401, 
            detail="Refresh token revoked or expired"
        )
    
    await db.delete(token_record)
    await db.commit()

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
    Docstring для logout
    
    :param logout_data: Описание
    :type logout_data: TokenRefreshRequest
    :param db: Описание
    :type db: AsyncSession
    """
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == logout_data.refresh_token))
    token_record = result.scalar_one_or_none()

    if token_record:
        await db.delete(token_record)
        await db.commit()

    return {"message": "Successfully logged out"}