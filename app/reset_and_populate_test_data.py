"""
Database Reset and Test Data Population Script.

This script:
1. Drops all tables from the database
2. Recreates all tables
3. Populates with test users, permissions, and business elements

Test credentials (all users have password: 'password123'):
- admin@example.com (role: admin)
- ivan@example.com (role: user)
- maria@example.com (role: moderator)
- alexey@example.com (role: user)
- elena@example.com (role: manager)

Usage:
    python reset_and_populate_test_data.py
"""

import asyncio
import sys
import os

# Add project path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.database import engine, Base
from database.models_db import User, Permissions, BusinessElements
from tools.hash import get_password_hash


async def reset_database():
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all existing data!
    """
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Recreate all tables
        await conn.run_sync(Base.metadata.create_all)


async def create_test_users():
    """
    Create test users in the database.
    
    Skips if users already exist (idempotent operation).
    """
    async with AsyncSession(engine) as session:
        # Check if users already exist
        result = await session.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            print("Test users already exist. Skipping creation.")
            return

        # Create test users
        test_users = [
            {
                "first_name": "Admin",
                "last_name": "Adminov",
                "patronymic": "Adminovich",
                "email": "admin@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "admin"
            },
            {
                "first_name": "John",
                "last_name": "Ivanov",
                "patronymic": "Ivanovich",
                "email": "ivan@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "user"
            },
            {
                "first_name": "Maria",
                "last_name": "Petrova",
                "patronymic": "Sergeevna",
                "email": "maria@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "moderator"
            },
            {
                "first_name": "Alexey",
                "last_name": "Sidorov",
                "patronymic": None,
                "email": "alexey@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "user"
            },
            {
                "first_name": "Elena",
                "last_name": "Kuznetsova",
                "patronymic": "Vladimirovna",
                "email": "elena@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "manager"
            }
        ]

        for user_data in test_users:
            user = User(**user_data)
            session.add(user)

        await session.commit()
        print(f"Created {len(test_users)} test users")


async def create_test_permissions():
    """
    Create test permission records for different roles.
    
    Skips if permissions already exist (idempotent operation).
    
    Roles created:
    - admin: Full access to all resources
    - moderator: Read/update users, read permissions, create/update business elements
    - manager: Read all users, update users, full access to business elements (except delete)
    - user: Basic read access only
    """
    async with AsyncSession(engine) as session:
        # Check if permissions already exist
        result = await session.execute(select(Permissions))
        existing_permissions = result.scalars().all()

        if existing_permissions:
            print("Test permissions already exist. Skipping creation.")
            return

        # Create test permissions for different roles
        test_permissions = [
            {
                "role_name": "admin",
                # CRUD users
                "create_users": True,
                "read_users": True,
                "read_all_users": True,
                "update_users": True,
                "delete_users": True,
                # CRUD permissions
                "create_permissions": True,
                "read_permissions": True,
                "read_all_permissions": True,
                "update_permissions": True,
                "delete_permissions": True,
                # CRUD business_elements
                "create_business_elements": True,
                "read_business_elements": True,
                "read_all_business_elements": True,
                "update_business_elements": True,
                "delete_business_elements": True
            },
            {
                "role_name": "moderator",
                # CRUD users
                "create_users": False,
                "read_users": True,
                "read_all_users": False,
                "update_users": True,
                "delete_users": False,
                # CRUD permissions
                "create_permissions": False,
                "read_permissions": True,
                "read_all_permissions": False,
                "update_permissions": False,
                "delete_permissions": False,
                # CRUD business_elements
                "create_business_elements": True,
                "read_business_elements": True,
                "read_all_business_elements": False,
                "update_business_elements": True,
                "delete_business_elements": False
            },
            {
                "role_name": "manager",
                # CRUD users
                "create_users": False,
                "read_users": True,
                "read_all_users": True,
                "update_users": True,
                "delete_users": False,
                # CRUD permissions
                "create_permissions": False,
                "read_permissions": True,
                "read_all_permissions": False,
                "update_permissions": False,
                "delete_permissions": False,
                # CRUD business_elements
                "create_business_elements": True,
                "read_business_elements": True,
                "read_all_business_elements": True,
                "update_business_elements": True,
                "delete_business_elements": False
            },
            {
                "role_name": "user",
                # CRUD users
                "create_users": False,
                "read_users": True,
                "read_all_users": False,
                "update_users": False,
                "delete_users": False,
                # CRUD permissions
                "create_permissions": False,
                "read_permissions": True,
                "read_all_permissions": False,
                "update_permissions": False,
                "delete_permissions": False,
                # CRUD business_elements
                "create_business_elements": False,
                "read_business_elements": True,
                "read_all_business_elements": False,
                "update_business_elements": False,
                "delete_business_elements": False
            }
        ]

        for perm_data in test_permissions:
            permission = Permissions(**perm_data)
            session.add(permission)

        await session.commit()
        print(f"Created {len(test_permissions)} permission records")


async def create_test_business_elements():
    """
    Create test business elements.
    
    Skips if business elements already exist (idempotent operation).
    """
    async with AsyncSession(engine) as session:
        # Check if business elements already exist
        result = await session.execute(select(BusinessElements))
        existing_elements = result.scalars().all()

        if existing_elements:
            print("Test business elements already exist. Skipping creation.")
            return

        # Create test business elements
        test_elements = [
            {
                "name": "Product 1",
                "roles": ["admin", "moderator", "manager"],
                "description": "Description for Product 1"
            },
            {
                "name": "Product 2",
                "roles": ["admin", "moderator"],
                "description": "Description for Product 2"
            },
            {
                "name": "Service 1",
                "roles": ["admin", "manager", "user"],
                "description": "Description for Service 1"
            },
            {
                "name": "Project A",
                "roles": ["admin", "manager"],
                "description": "Description for Project A"
            },
            {
                "name": "Project B",
                "roles": ["admin", "moderator", "manager"],
                "description": "Description for Project B"
            }
        ]

        for element_data in test_elements:
            element = BusinessElements(**element_data)
            session.add(element)

        await session.commit()
        print(f"Created {len(test_elements)} test business elements")


async def main():
    """
    Main function to reset database and populate with test data.
    """
    print("Starting database reset and test data population...")

    # Reset database and create tables
    await reset_database()

    # Create test users
    await create_test_users()

    # Create test permissions
    await create_test_permissions()

    # Create test business elements
    await create_test_business_elements()

    print("Database reset and test data population completed!")


if __name__ == "__main__":
    asyncio.run(main())
