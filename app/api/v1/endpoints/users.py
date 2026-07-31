from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import User, Department, Job
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User / Employee Record",
    description="""
Create a new employee or manager user in the database.
Businesses can include any dynamic enterprise schema attributes inside the `custom_metadata` object.
""",
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    existing_users = await repo.get_all(email=user_in.email)
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    title_input = user_in.job_title or user_in.role
    if title_input and not user_in.job_id:
        job_repo = SQLAlchemyRepository(Job, db)
        jobs = await job_repo.get_all(job_title=title_input)
        if jobs:
            user_in.job_id = jobs[0].id

    if user_in.department and not user_in.department_id:
        dept_repo = SQLAlchemyRepository(Department, db)
        depts = await dept_repo.get_all(name=user_in.department)
        if depts:
            user_in.department_id = depts[0].id

    return await repo.create(user_in)


@router.post(
    "/sync",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync Authenticated User Profile (Google / Facebook / Email)",
    description="""
Upserts a user profile into the database upon successful OAuth sign-in (Google, Facebook, or Password).
If the user exists by email, updates their info and custom metadata. Otherwise creates a new record.
""",
)
async def sync_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    existing_users = await repo.get_all(email=user_in.email)

    title_input = user_in.job_title or user_in.role
    if title_input and not user_in.job_id:
        job_repo = SQLAlchemyRepository(Job, db)
        jobs = await job_repo.get_all(job_title=title_input)
        if jobs:
            user_in.job_id = jobs[0].id

    if user_in.department and not user_in.department_id:
        dept_repo = SQLAlchemyRepository(Department, db)
        depts = await dept_repo.get_all(name=user_in.department)
        if depts:
            user_in.department_id = depts[0].id

    if existing_users:
        existing_user = existing_users[0]
        merged_metadata = dict(existing_user.custom_metadata or {})
        merged_metadata.update(user_in.custom_metadata or {})
        
        update_data = {
            "first_name": user_in.first_name or existing_user.first_name,
            "last_name": user_in.last_name or existing_user.last_name,
            "job_id": user_in.job_id or existing_user.job_id,
            "department_id": user_in.department_id or existing_user.department_id,
            "photo_url": user_in.photo_url if user_in.photo_url is not None else existing_user.photo_url,
            "custom_metadata": merged_metadata
        }
        updated = await repo.update(existing_user.id, update_data)
        return updated
    return await repo.create(user_in)


@router.put(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Profile in Neon Database",
    description="Updates or creates a user profile in Neon PostgreSQL database by email address.",
)
async def update_profile(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    existing_users = await repo.get_all(email=user_in.email)

    update_fields = [
        "first_name", "last_name", "employee_id", "dob", "doh",
        "phone", "bio", "job_id", "department_id", "country", "city_state",
        "postal_code", "tax_id", "photo_url", "facebook", "x_link",
        "linkedin", "instagram"
    ]

    title_input = user_in.job_title or user_in.role
    if title_input and not user_in.job_id:
        job_repo = SQLAlchemyRepository(Job, db)
        jobs = await job_repo.get_all(job_title=title_input)
        if jobs:
            user_in.job_id = jobs[0].id

    if user_in.department and not user_in.department_id:
        dept_repo = SQLAlchemyRepository(Department, db)
        depts = await dept_repo.get_all(name=user_in.department)
        if depts:
            user_in.department_id = depts[0].id

    if existing_users:
        existing_user = existing_users[0]
        merged_metadata = dict(existing_user.custom_metadata or {})
        if user_in.custom_metadata:
            merged_metadata.update(user_in.custom_metadata)

        update_dict: Dict[str, Any] = {
            "custom_metadata": merged_metadata
        }
        for field in update_fields:
            val = getattr(user_in, field, None)
            if val is not None:
                update_dict[field] = val

        updated = await repo.update(existing_user.id, update_dict)
        return updated

    create_kwargs = {
        "email": user_in.email,
        "custom_metadata": user_in.custom_metadata or {},
    }
    for field in update_fields:
        val = getattr(user_in, field, None)
        if val is not None:
            create_kwargs[field] = val

    create_data = UserCreate(**create_kwargs)
    return await repo.create(create_data)


@router.get(
    "/by-email/{email}",
    response_model=UserResponse,
    summary="Get User Profile by Email",
    description="Fetch user profile and enterprise custom metadata from Neon PostgreSQL by email address.",
)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    users = await repo.get_all(email=email)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found in Neon database.",
        )
    return users[0]


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List Users / Employees",
    description="""
Retrieve a paginated list of users with optional filtering by department or role.
""",
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max number of items to return"),
    department: Optional[str] = Query(None, description="Filter users by department"),
    role: Optional[str] = Query(None, description="Filter users by role"),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    filters = {}
    if department:
        filters["department"] = department
    if role:
        filters["role"] = role
    return await repo.get_all(skip=skip, limit=limit, **filters)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User Details",
    description="Fetch full details and enterprise custom metadata for a specific user ID.",
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(User, db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
        )
    return user
