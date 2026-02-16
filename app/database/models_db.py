from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSON
from database.database import Base
import datetime

class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    patronymic = Column(String(30), default=None, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Дополнительные поля
    is_active = Column(Boolean, default=True)
    is_role = Column(String(50), default="user") 


class Permissions(Base):
    """Модель прав доступа"""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)  

    # CRUD users
    create_users = Column(Boolean, default=False)
    read_users = Column(Boolean, default=False)
    read_all_users = Column(Boolean, default=False)
    update_users = Column(Boolean, default=False)
    delete_users = Column(Boolean, default=False)

    # CRUD permissions
    create_permissions = Column(Boolean, default=False)
    read_permissions = Column(Boolean, default=False)
    read_all_permissions = Column(Boolean, default=False)
    update_permissions = Column(Boolean, default=False)
    delete_permissions = Column(Boolean, default=False)

    # CRUD busines_elements
    create_busines_elements = Column(Boolean, default=False)
    read_busines_elements = Column(Boolean, default=False)
    read_all_busines_elements = Column(Boolean, default=False)
    update_busines_elements = Column(Boolean, default=False)
    delete_busines_elements = Column(Boolean, default=False)


class BusinesElements(Base):
    """Модель бизнес-элементов"""

    __tablename__ = "busines_elements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    roles = Column(JSON, nullable=False) 

    
    description = Column(String(255), nullable=True) 


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
