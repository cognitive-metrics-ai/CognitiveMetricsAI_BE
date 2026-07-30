from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Role
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[RoleResponse],
    summary="List Roles",
    description="Retrieve list of organizational roles.",
)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Role, db)
    return await repo.get_all(skip=skip, limit=limit)


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Role",
    description="Creates a new role record with role_id and name.",
)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Role, db)
    existing_code = await repo.get_all(role_id=role_in.role_id)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with role_id '{role_in.role_id}' already exists.",
        )
    existing_name = await repo.get_all(name=role_in.name)
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.name}' already exists.",
        )
    return await repo.create(role_in)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get Role Details",
    description="Fetch single role record by database UUID or role_id.",
)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Role, db)
    role_obj = await repo.get_by_id(role_id)
    if not role_obj:
        by_code = await repo.get_all(role_id=role_id)
        if by_code:
            return by_code[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_id}' not found.",
        )
    return role_obj


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update Role Record",
    description="Update role details.",
)
async def update_role(
    role_id: str,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Role, db)
    role_obj = await repo.get_by_id(role_id)
    if not role_obj:
        by_code = await repo.get_all(role_id=role_id)
        if by_code:
            role_obj = by_code[0]

    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_id}' not found.",
        )

    return await repo.update(role_obj.id, role_in)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Role Record",
    description="Removes a role record.",
)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Role, db)
    role_obj = await repo.get_by_id(role_id)
    if not role_obj:
        by_code = await repo.get_all(role_id=role_id)
        if by_code:
            role_obj = by_code[0]

    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_id}' not found.",
        )

    await repo.delete(role_obj.id)
    return None
