from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Department
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[DepartmentResponse],
    summary="List Departments",
    description="Retrieve list of departments.",
)
async def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Department, db)
    return await repo.get_all(skip=skip, limit=limit)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Department",
    description="Creates a new department record with department_id and name.",
)
async def create_department(
    dept_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Department, db)
    existing_code = await repo.get_all(department_id=dept_in.department_id)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with department_id '{dept_in.department_id}' already exists.",
        )
    existing_name = await repo.get_all(name=dept_in.name)
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with name '{dept_in.name}' already exists.",
        )
    return await repo.create(dept_in)


@router.get(
    "/{dept_id}",
    response_model=DepartmentResponse,
    summary="Get Department Details",
    description="Fetch single department record by database UUID or department_id.",
)
async def get_department(
    dept_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Department, db)
    dept = await repo.get_by_id(dept_id)
    if not dept:
        by_code = await repo.get_all(department_id=dept_id)
        if by_code:
            return by_code[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{dept_id}' not found.",
        )
    return dept


@router.put(
    "/{dept_id}",
    response_model=DepartmentResponse,
    summary="Update Department Record",
    description="Update department details.",
)
async def update_department(
    dept_id: str,
    dept_in: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Department, db)
    dept = await repo.get_by_id(dept_id)
    if not dept:
        by_code = await repo.get_all(department_id=dept_id)
        if by_code:
            dept = by_code[0]

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{dept_id}' not found.",
        )

    return await repo.update(dept.id, dept_in)


@router.delete(
    "/{dept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Department Record",
    description="Removes a department record.",
)
async def delete_department(
    dept_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Department, db)
    dept = await repo.get_by_id(dept_id)
    if not dept:
        by_code = await repo.get_all(department_id=dept_id)
        if by_code:
            dept = by_code[0]

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{dept_id}' not found.",
        )

    await repo.delete(dept.id)
    return None
