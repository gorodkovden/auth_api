from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database.models_db import BusinesElements, User
from tools.auth_func import require_permission, get_current_user
from database.database import get_db
from tools.shemas import BusinesElementCreate, BusinesElementResponse, BusinesElementObject

busines_elements_router = APIRouter(prefix="/busines-elements", tags=["Business Elements"])

@busines_elements_router.get("/", response_model=List[BusinesElementResponse])
async def get_all_busines_elements(current_user: User = Depends(require_permission("busines_elements", "read_all")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить список всех бизнес-элементов (требуется разрешение на чтение всех элементов)
    """

    result = await db.execute(select(BusinesElements))
    elements = result.scalars().all()

    return [
        {
            "id": element.id,
            "name": element.name,
            "roles": element.roles
        }
        for element in elements
    ]


@busines_elements_router.get("/{element_name}", response_model=BusinesElementResponse)
async def get_busines_element(element_name: str, current_user: User = Depends(require_permission("busines_elements", "read")), db: AsyncSession = Depends(get_db)):
    
    """
    Получить информацию о конкретном бизнес-элементе (требуется разрешение на чтение элементов)
    """

    result = await db.execute(select(BusinesElements).filter(BusinesElements.name == element_name))
    element = result.scalar_one_or_none()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found"
        )

    return {
        "id": element.id,
        "name": element.name,
        "roles": element.roles
    }


@busines_elements_router.post("/", response_model=BusinesElementResponse)
async def create_busines_element(element_data: BusinesElementCreate, current_user: User = Depends(require_permission("busines_elements", "create")), db: AsyncSession = Depends(get_db)):

    """
    Создать новый бизнес-элемент (требуется разрешение на создание элементов)
    """

    result = await db.execute(select(BusinesElements).filter(BusinesElements.name == element_data.name))
    existing_element = result.scalar_one_or_none()

    if existing_element:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business element with this name already exists"
        )

    db_element = BusinesElements(
        name=element_data.name,
        roles=element_data.roles
    )

    db.add(db_element)
    await db.commit()
    await db.refresh(db_element)

    return {
        "id": db_element.id,
        "name": db_element.name,
        "roles": db_element.roles
    }


@busines_elements_router.put("/{element_name}", response_model=BusinesElementResponse)
async def update_busines_element(element_data: BusinesElementCreate, current_user: User = Depends(require_permission("busines_elements", "update")), db: AsyncSession = Depends(get_db)):
    
    """
    Обновить бизнес-элемент (требуется разрешение на обновление элементов)
    """

    result = await db.execute(select(BusinesElements).filter(BusinesElements.name == element_data.name))
    element = result.scalar_one_or_none()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found"
        )

    element.name = element_data.name
    element.roles = element_data.roles
    await db.commit()
    await db.refresh(element) 
    
    return {
        "id": element.id,
        "name": element.name,
        "roles": element.roles
    }


@busines_elements_router.delete("/{element_name}", response_model=BusinesElementResponse)
async def delete_busines_element(element_name: str, current_user: User = Depends(require_permission("busines_elements", "delete")), db: AsyncSession = Depends(get_db)):
    
    """
    Удалить бизнес-элемент (требуется разрешение на удаление элементов)
    """

    result = await db.execute(select(BusinesElements).filter(BusinesElements.name == element_name))
    element = result.scalar_one_or_none()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found"
        )

    await db.delete(element)
    await db.commit()

    return {
        "id": element.id, 
        "name": element.name, 
        "roles": element.roles
    }


# Mock-view
@busines_elements_router.get("/{element_name}/", response_model=BusinesElementObject)
async def view_busines_element_object(element_name: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(BusinesElements).filter(BusinesElements.name == element_name))
    element = result.scalar_one_or_none()
    result = await db.execute(select(User).filter(User.id == current_user))
    user_data = result.scalar_one_or_none()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found"
        )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_data.is_role not in element.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Role '{user_data.is_role}' does not have permission to view this element."
        )

    return {
        "description": element.description
    }


