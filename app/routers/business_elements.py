"""
Business Elements Management Router.

Endpoints for managing business elements:
- List all business elements
- Get business element by name
- Create new business element
- Update business element
- Delete business element
- View element object (with role-based access check)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database.models_db import BusinessElements, User
from tools.auth_func import require_permission, get_current_user
from database.database import get_db
from tools.schemas import BusinessElementCreate, BusinessElementResponse, BusinessElementObject

business_elements_router = APIRouter(prefix="/business-elements", tags=["Business Elements"])


@business_elements_router.get("/", response_model=List[BusinessElementResponse])
async def get_all_business_elements(
    current_user: User = Depends(require_permission("business_elements", "read_all")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all business elements.
    
    Args:
        current_user: Authenticated user (requires 'read_all' permission for business_elements)
        db: Database session
        
    Returns:
        List[BusinessElementResponse]: List of all business elements
        
    Raises:
        HTTPException: 403 if user lacks 'read_all' permission
    """
    result = await db.execute(select(BusinessElements))
    elements = result.scalars().all()

    return [
        {
            "id": element.id,
            "name": element.name,
            "roles": element.roles
        }
        for element in elements
    ]


@business_elements_router.get("/{element_name}", response_model=BusinessElementResponse)
async def get_business_element(
    element_name: str,
    current_user: User = Depends(require_permission("business_elements", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get business element by name.
    
    Args:
        element_name: Name of the element to retrieve
        current_user: Authenticated user (requires 'read' permission for business_elements)
        db: Database session
        
    Returns:
        BusinessElementResponse: Business element details
        
    Raises:
        HTTPException: 404 if element not found
        HTTPException: 403 if user lacks 'read' permission
    """
    result = await db.execute(select(BusinessElements).filter(BusinessElements.name == element_name))
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


@business_elements_router.post("/", response_model=BusinessElementResponse)
async def create_business_element(
    element_data: BusinessElementCreate,
    current_user: User = Depends(require_permission("business_elements", "create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new business element.
    
    Args:
        element_data: Business element data (name, roles)
        current_user: Authenticated user (requires 'create' permission for business_elements)
        db: Database session
        
    Returns:
        BusinessElementResponse: Created business element
        
    Raises:
        HTTPException: 409 if element with name already exists
        HTTPException: 403 if user lacks 'create' permission
    """
    # Check if element already exists
    result = await db.execute(select(BusinessElements).filter(BusinessElements.name == element_data.name))
    existing_element = result.scalar_one_or_none()

    if existing_element:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business element with this name already exists"
        )

    # Create new element
    db_element = BusinessElements(
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


@business_elements_router.put("/{element_name}", response_model=BusinessElementResponse)
async def update_business_element(
    element_data: BusinessElementCreate,
    current_user: User = Depends(require_permission("business_elements", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a business element.
    
    Args:
        element_data: New business element data
        current_user: Authenticated user (requires 'update' permission for business_elements)
        db: Database session
        
    Returns:
        BusinessElementResponse: Updated business element
        
    Raises:
        HTTPException: 404 if element not found
        HTTPException: 403 if user lacks 'update' permission
    """
    result = await db.execute(select(BusinessElements).filter(BusinessElements.name == element_data.name))
    element = result.scalar_one_or_none()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found"
        )

    # Update element fields
    element.name = element_data.name
    element.roles = element_data.roles
    await db.commit()
    await db.refresh(element)

    return {
        "id": element.id,
        "name": element.name,
        "roles": element.roles
    }


@business_elements_router.delete("/{element_name}", response_model=BusinessElementResponse)
async def delete_business_element(
    element_name: str,
    current_user: User = Depends(require_permission("business_elements", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a business element.
    
    Args:
        element_name: Name of the element to delete
        current_user: Authenticated user (requires 'delete' permission for business_elements)
        db: Database session
        
    Returns:
        BusinessElementResponse: Deleted business element data
        
    Raises:
        HTTPException: 404 if element not found
        HTTPException: 403 if user lacks 'delete' permission
    """
    result = await db.execute(select(BusinessElements).filter(BusinessElements.name == element_name))
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


@business_elements_router.get("/{element_name}/", response_model=BusinessElementObject)
async def view_business_element_object(
    element_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View business element object (with role-based access control).
    
    This endpoint checks if the current user's role has access to view
    this specific business element.
    
    Args:
        element_name: Name of the element to view
        current_user: Authenticated user (any valid token)
        db: Database session
        
    Returns:
        BusinessElementObject: Element description
        
    Raises:
        HTTPException: 404 if element or user not found
        HTTPException: 403 if user's role doesn't have access
    """
    # Get business element
    result = await db.execute(select(BusinessElements).filter(BusinessElements.name == element_name))
    element = result.scalar_one_or_none()
    
    # Get current user data
    result = await db.execute(select(User).filter(User.id == current_user.id))
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

    # Check if user's role has access to this element
    if user_data.is_role not in element.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Role '{user_data.is_role}' does not have permission to view this element."
        )

    return {
        "description": element.description
    }
