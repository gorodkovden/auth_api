from pydantic import BaseModel, Field
from typing import List


# ==============  Аутентификация ==============
class UserRegister(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=30)
    last_name: str = Field(..., min_length=2, max_length=30)
    patronymic: str = Field(..., max_length=30)
    email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=30)
    password_confirm: str = Field(..., min_length=6, max_length=30)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'

class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ==============  Права доступа ==============
class PermissionCreate(BaseModel):
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

    # CRUD busines_elements
    create_busines_elements: bool = False
    read_busines_elements: bool = False
    read_all_busines_elements: bool = False
    update_busines_elements: bool = False
    delete_busines_elements: bool = False


class PermissionResponse(BaseModel):
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

    # CRUD busines_elements
    create_busines_elements: bool
    read_busines_elements: bool
    read_all_busines_elements: bool
    update_busines_elements: bool
    delete_busines_elements: bool

# ==============  Бизнес-элементы ==============
class BusinesElementCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    roles: List[str] = Field(..., min_items=1)

class BusinesElementResponse(BaseModel):
    id: int
    name: str
    roles: List[str]

class BusinesElementObject(BaseModel):
    description: str
