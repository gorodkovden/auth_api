"""
Pydantic Schemas for Request/Response Validation.

This module defines data schemas for:
- User authentication (register, login, tokens)
- Permissions (create, read, update, delete)
- Business elements (create, read, update, delete)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


# ============== Authentication Schemas ==============

class UserRegister(BaseModel):
    """
    Schema for user registration request.
    
    Attributes:
        first_name: User's first name (2-30 chars)
        last_name: User's last name (2-30 chars)
        patronymic: User's middle name (optional, max 30 chars)
        email: Valid email address (3-100 chars)
        password: Password (6-30 chars)
        password_confirm: Password confirmation (must match password)
    """
    first_name: str = Field(..., min_length=2, max_length=30)
    last_name: str = Field(..., min_length=2, max_length=30)
    patronymic: Optional[str] = Field(None, max_length=30)
    email: EmailStr = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=30)
    password_confirm: str = Field(..., min_length=6, max_length=30)


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Attributes:
        email: User's email address
        password: User's password
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Schema for token response after login/refresh.
    
    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (always 'Bearer')
    """
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'


class TokenRefreshRequest(BaseModel):
    """
    Schema for refresh token request.
    
    Attributes:
        refresh_token: JWT refresh token to exchange for new tokens
    """
    refresh_token: str


class TokenLogoutRequest(BaseModel):
    """
    Schema for logout request.
    
    Attributes:
        refresh_token: JWT refresh token to revoke
    """
    refresh_token: str


# ============== Permissions Schemas ==============

class PermissionCreate(BaseModel):
    """
    Schema for creating/updating permissions.
    
    Attributes:
        role_name: Unique role name (1-50 chars)
        create_users: Permission to create users
        read_users: Permission to read own user data
        read_all_users: Permission to read all users
        update_users: Permission to update users
        delete_users: Permission to delete users
        create_permissions: Permission to create permissions
        read_permissions: Permission to read permissions
        read_all_permissions: Permission to read all permissions
        update_permissions: Permission to update permissions
        delete_permissions: Permission to delete permissions
        create_business_elements: Permission to create business elements
        read_business_elements: Permission to read business elements
        read_all_business_elements: Permission to read all business elements
        update_business_elements: Permission to update business elements
        delete_business_elements: Permission to delete business elements
    """
    role_name: str = Field(..., min_length=1, max_length=50)

    # CRUD users
    create_users: bool = False
    read_users: bool = False
    read_all_users: bool = False
    update_users: bool = False
    delete_users: bool = False

    # CRUD permissions
    create_permissions: bool = False
    read_permissions: bool = False
    read_all_permissions: bool = False
    update_permissions: bool = False
    delete_permissions: bool = False

    # CRUD business_elements
    create_business_elements: bool = False
    read_business_elements: bool = False
    read_all_business_elements: bool = False
    update_business_elements: bool = False
    delete_business_elements: bool = False


class PermissionResponse(BaseModel):
    """
    Schema for permission response.
    
    Attributes:
        id: Permission record ID
        role_name: Role name
        create_users: Permission to create users
        read_users: Permission to read own user data
        read_all_users: Permission to read all users
        update_users: Permission to update users
        delete_users: Permission to delete users
        create_permissions: Permission to create permissions
        read_permissions: Permission to read permissions
        read_all_permissions: Permission to read all permissions
        update_permissions: Permission to update permissions
        delete_permissions: Permission to delete permissions
        create_business_elements: Permission to create business elements
        read_business_elements: Permission to read business elements
        read_all_business_elements: Permission to read all business elements
        update_business_elements: Permission to update business elements
        delete_business_elements: Permission to delete business elements
    """
    id: int
    role_name: str

    # CRUD users
    create_users: bool
    read_users: bool
    read_all_users: bool
    update_users: bool
    delete_users: bool

    # CRUD permissions
    create_permissions: bool
    read_permissions: bool
    read_all_permissions: bool
    update_permissions: bool
    delete_permissions: bool

    # CRUD business_elements
    create_business_elements: bool
    read_business_elements: bool
    read_all_business_elements: bool
    update_business_elements: bool
    delete_business_elements: bool


# ============== Business Elements Schemas ==============

class BusinessElementCreate(BaseModel):
    """
    Schema for creating/updating business elements.
    
    Attributes:
        name: Unique element name (1-100 chars)
        roles: List of role names that can access this element
    """
    name: str = Field(..., min_length=1, max_length=100)
    roles: List[str] = Field(..., min_length=1)
    description: str = Field(..., min_length=1, max_length=255)


class BusinessElementResponse(BaseModel):
    """
    Schema for business element response.
    
    Attributes:
        id: Element ID
        name: Element name
        roles: List of role names that can access this element
    """
    id: int
    name: str
    roles: List[str]


class BusinessElementObject(BaseModel):
    """
    Schema for business element object view.
    
    Attributes:
        description: Element description
    """
    id: int
    name: str
    roles: str
    description: str
