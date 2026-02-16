"""
Database models for the Authentication API.

This module defines SQLAlchemy ORM models for:
- User authentication and profiles
- Role-based permissions
- Business elements with role access
- Refresh token storage
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSON
from database.database import Base
import datetime


class User(Base):
    """
    User model for authentication and profile management.
    
    Attributes:
        id: Primary key
        first_name: User's first name (max 30 chars)
        last_name: User's last name (max 30 chars)
        patronymic: User's middle name (optional, max 30 chars)
        email: Unique email address (used for login)
        hashed_password: Bcrypt-hashed password
        is_active: Account status (active/inactive)
        is_role: User's role name (e.g., 'admin', 'user', 'moderator')
    """

    __tablename__ = "users"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    patronymic = Column(String(30), default=None, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Additional fields
    is_active = Column(Boolean, default=True)
    is_role = Column(String(50), default="user")


class Permissions(Base):
    """
    Permissions model for role-based access control (RBAC).
    
    Defines CRUD permissions for three resources:
    - users: User management
    - permissions: Permission management
    - business_elements: Business element management
    
    Attributes:
        id: Primary key
        role_name: Unique role name
        create_*: Create permission flags
        read_*: Read single item permission flags
        read_all_*: Read all items permission flags
        update_*: Update permission flags
        delete_*: Delete permission flags
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    # CRUD users permissions
    create_users = Column(Boolean, default=False)
    read_users = Column(Boolean, default=False)
    read_all_users = Column(Boolean, default=False)
    update_users = Column(Boolean, default=False)
    delete_users = Column(Boolean, default=False)

    # CRUD permissions permissions
    create_permissions = Column(Boolean, default=False)
    read_permissions = Column(Boolean, default=False)
    read_all_permissions = Column(Boolean, default=False)
    update_permissions = Column(Boolean, default=False)
    delete_permissions = Column(Boolean, default=False)

    # CRUD business_elements permissions
    create_business_elements = Column(Boolean, default=False)
    read_business_elements = Column(Boolean, default=False)
    read_all_business_elements = Column(Boolean, default=False)
    update_business_elements = Column(Boolean, default=False)
    delete_business_elements = Column(Boolean, default=False)


class BusinessElements(Base):
    """
    Business elements model for storing application-specific data.
    
    Each element can be accessed by specific roles only.
    
    Attributes:
        id: Primary key
        name: Unique element name
        roles: JSON array of role names that can access this element
        description: Optional element description
    """

    __tablename__ = "business_elements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    roles = Column(JSON, nullable=False)
    description = Column(String(255), nullable=True)


class RefreshToken(Base):
    """
    Refresh token model for JWT token management.
    
    Stores refresh tokens in database for:
    - Token revocation on logout
    - Expiration tracking
    - Security audit
    
    Attributes:
        id: Primary key
        user_id: ID of the user who owns this token
        token: JWT refresh token string (unique)
        expires_at: Token expiration timestamp (UTC)
    """

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
