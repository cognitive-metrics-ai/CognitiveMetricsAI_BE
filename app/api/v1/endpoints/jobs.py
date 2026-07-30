from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Job, Competency
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import JobCreate, JobUpdate, JobResponse, CompetencyCreate, CompetencyResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[JobResponse],
    summary="List Jobs with Linked Competencies",
    description="Retrieve list of Core-HR Jobs with their linked Competencies.",
)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Job, db)
    return await repo.get_all(skip=skip, limit=limit)


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Job Profile & Linked Competencies",
    description="Creates a new job profile record with Job_ID, Job_Title, Job_Family, Job_Level, Job_Description, and linked Competencies.",
)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
):
    job_repo = SQLAlchemyRepository(Job, db)
    comp_repo = SQLAlchemyRepository(Competency, db)

    existing_code = await job_repo.get_all(job_id=job_in.job_id)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with job_id '{job_in.job_id}' already exists.",
        )
    existing_title = await job_repo.get_all(job_title=job_in.job_title)
    if existing_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with title '{job_in.job_title}' already exists.",
        )

    # Create Job Base
    job_data = job_in.model_dump(exclude={"competencies"})
    created_job = await job_repo.create(job_data)

    # Create linked Competencies
    if job_in.competencies:
        for c in job_in.competencies:
            c_data = c.model_dump()
            c_data["job_id"] = created_job.id
            await comp_repo.create(c_data)

    # Return created job with competencies
    return await job_repo.get_by_id(created_job.id)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get Job Profile Details",
    description="Fetch single job profile record with linked competencies by UUID or Job_ID.",
)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Job, db)
    job_obj = await repo.get_by_id(job_id)
    if not job_obj:
        by_code = await repo.get_all(job_id=job_id)
        if by_code:
            return by_code[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job_obj


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update Job Profile",
    description="Update job profile details.",
)
async def update_job(
    job_id: str,
    job_in: JobUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Job, db)
    job_obj = await repo.get_by_id(job_id)
    if not job_obj:
        by_code = await repo.get_all(job_id=job_id)
        if by_code:
            job_obj = by_code[0]

    if not job_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    return await repo.update(job_obj.id, job_in)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Job Profile",
    description="Removes a job profile record and its linked competencies.",
)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Job, db)
    job_obj = await repo.get_by_id(job_id)
    if not job_obj:
        by_code = await repo.get_all(job_id=job_id)
        if by_code:
            job_obj = by_code[0]

    if not job_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    await repo.delete(job_obj.id)
    return None
