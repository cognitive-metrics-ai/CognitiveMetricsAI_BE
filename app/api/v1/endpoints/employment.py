from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import WorkerEmployment, User
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import (
    WorkerEmploymentCreate,
    WorkerEmploymentUpdate,
    WorkerEmploymentResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[WorkerEmploymentResponse],
    summary="List Worker Employment Records",
    description="Retrieve list of Core-HR worker_employment records with Hire_Date, Termination_Date, Employment_Type, Work_Authorization, Union_Status, and FLSA_Status.",
)
async def list_employment_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    person_id: str = Query(None, description="Filter by person_id FK"),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(WorkerEmployment, db)
    filters = {}
    if person_id:
        filters["person_id"] = person_id
    return await repo.get_all(skip=skip, limit=limit, **filters)


@router.post(
    "/",
    response_model=WorkerEmploymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Worker Employment Record",
    description="Creates a new Core-HR worker_employment record linked to a Person (person_id).",
)
async def create_employment_record(
    employment_in: WorkerEmploymentCreate,
    db: AsyncSession = Depends(get_db),
):
    emp_repo = SQLAlchemyRepository(WorkerEmployment, db)
    user_repo = SQLAlchemyRepository(User, db)

    # Verify person_id user exists
    person = await user_repo.get_by_id(employment_in.person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person (User) with id '{employment_in.person_id}' not found.",
        )

    # Check for duplicate worker_id
    existing_wrk = await emp_repo.get_all(worker_id=employment_in.worker_id)
    if existing_wrk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker employment record with worker_id '{employment_in.worker_id}' already exists.",
        )

    return await emp_repo.create(employment_in)


@router.get(
    "/{employment_id}",
    response_model=WorkerEmploymentResponse,
    summary="Get Worker Employment Record Details",
    description="Fetch single worker_employment record by UUID or worker_id.",
)
async def get_employment_record(
    employment_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(WorkerEmployment, db)
    record = await repo.get_by_id(employment_id)
    if not record:
        by_wrk = await repo.get_all(worker_id=employment_id)
        if by_wrk:
            return by_wrk[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker employment record '{employment_id}' not found.",
        )
    return record


@router.put(
    "/{employment_id}",
    response_model=WorkerEmploymentResponse,
    summary="Update Worker Employment Record",
    description="Update worker employment details.",
)
async def update_employment_record(
    employment_id: str,
    employment_in: WorkerEmploymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(WorkerEmployment, db)
    record = await repo.get_by_id(employment_id)
    if not record:
        by_wrk = await repo.get_all(worker_id=employment_id)
        if by_wrk:
            record = by_wrk[0]

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker employment record '{employment_id}' not found.",
        )

    return await repo.update(record.id, employment_in)


@router.delete(
    "/{employment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Worker Employment Record",
    description="Deletes a worker_employment record.",
)
async def delete_employment_record(
    employment_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(WorkerEmployment, db)
    record = await repo.get_by_id(employment_id)
    if not record:
        by_wrk = await repo.get_all(worker_id=employment_id)
        if by_wrk:
            record = by_wrk[0]

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker employment record '{employment_id}' not found.",
        )

    await repo.delete(record.id)
    return None
