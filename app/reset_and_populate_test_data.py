"""
Скрипт для сброса и заполнения базы данных тестовыми данными
"""
import asyncio
import sys
import os

# Добавляем путь к проекту для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.database import engine, Base
from database.models_db import User, Permissions, BusinesElements
from tools.hash import get_password_hash


async def reset_database():
    """Сброс базы данных и создание таблиц"""
    async with engine.begin() as conn:
        # Удаляем все таблицы
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем все таблицы заново
        await conn.run_sync(Base.metadata.create_all)


async def create_test_users():
    """Создание тестовых пользователей"""
    async with AsyncSession(engine) as session:
        # Проверяем, есть ли уже пользователи
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        
        if existing_users:
            print("Тестовые пользователи уже существуют. Пропускаем создание.")
            return
        
        # Создаем тестовых пользователей
        test_users = [
            {
                "first_name": "Админ",
                "last_name": "Админов",
                "patronymic": "Админович",
                "email": "admin@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "admin"
            },
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "patronymic": "Иванович",
                "email": "ivan@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "user"
            },
            {
                "first_name": "Мария",
                "last_name": "Петрова",
                "patronymic": "Сергеевна",
                "email": "maria@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "moderator"
            },
            {
                "first_name": "Алексей",
                "last_name": "Сидоров",
                "patronymic": None,
                "email": "alexey@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "user"
            },
            {
                "first_name": "Елена",
                "last_name": "Кузнецова",
                "patronymic": "Владимировна",
                "email": "elena@example.com",
                "hashed_password": get_password_hash("password123"),
                "is_role": "manager"
            }
        ]
        
        for user_data in test_users:
            user = User(**user_data)
            session.add(user)
        
        await session.commit()
        print(f"Создано {len(test_users)} тестовых пользователей")


async def create_test_permissions():
    """Создание тестовых прав доступа"""
    async with AsyncSession(engine) as session:
        # Проверяем, есть ли уже права доступа
        result = await session.execute(select(Permissions))
        existing_permissions = result.scalars().all()

        if existing_permissions:
            print("Тестовые права доступа уже существуют. Пропускаем создание.")
            return

        # Создаем тестовые права доступа для разных ролей
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

                # CRUD busines_elements
                "create_busines_elements": True,
                "read_busines_elements": True,
                "read_all_busines_elements": True,
                "update_busines_elements": True,
                "delete_busines_elements": True
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

                # CRUD busines_elements
                "create_busines_elements": True,
                "read_busines_elements": True,
                "read_all_busines_elements": False,
                "update_busines_elements": True,
                "delete_busines_elements": False
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

                # CRUD busines_elements
                "create_busines_elements": True,
                "read_busines_elements": True,
                "read_all_busines_elements": True,
                "update_busines_elements": True,
                "delete_busines_elements": False
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
                
                # CRUD busines_elements
                "create_busines_elements": False,
                "read_busines_elements": True,
                "read_all_busines_elements": False,
                "update_busines_elements": False,
                "delete_busines_elements": False
            }
        ]

        for perm_data in test_permissions:
            permission = Permissions(**perm_data)
            session.add(permission)

        await session.commit()
        print(f"Создано {len(test_permissions)} записей прав доступа")


async def create_test_business_elements():
    """Создание тестовых бизнес-элементов"""
    async with AsyncSession(engine) as session:
        # Проверяем, есть ли уже бизнес-элементы
        result = await session.execute(select(BusinesElements))
        existing_elements = result.scalars().all()

        if existing_elements:
            print("Тестовые бизнес-элементы уже существуют. Пропускаем создание.")
            return

        # Создаем тестовые бизнес-элементы
        test_elements = [
            {
                "name": "Продукт 1",
                "roles": ["admin", "moderator", "manager"],
                "description": "Описание продукта 1"
            },
            {
                "name": "Продукт 2",
                "roles": ["admin", "moderator"],
                "description": "Описание продукта 2"
            },
            {
                "name": "Услуга 1",
                "roles": ["admin", "manager", "user"],
                "description": "Описание услуги 1"
            },
            {
                "name": "Проект A",
                "roles": ["admin", "manager"],
                "description": "Описание проекта A"
            },
            {
                "name": "Проект B",
                "roles": ["admin", "moderator", "manager"],
                "description": "Описание проекта B"
            }
        ]

        for element_data in test_elements:
            element = BusinesElements(**element_data)
            session.add(element)

        await session.commit()
        print(f"Создано {len(test_elements)} тестовых бизнес-элементов")


async def main():
    """Основная функция для сброса и заполнения базы данных тестовыми данными"""
    print("Начинаем сброс и заполнение базы данных тестовыми данными...")

    # Сбрасываем и создаем таблицы
    await reset_database()

    # Создаем тестовых пользователей
    await create_test_users()

    # Создаем тестовые права доступа
    await create_test_permissions()

    # Создаем тестовые бизнес-элементы
    await create_test_business_elements()

    print("Сброс и заполнение тестовыми данными завершено!")

if __name__ == "__main__":
    asyncio.run(main())