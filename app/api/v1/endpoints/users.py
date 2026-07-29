from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import User
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import UserCreate, UserResponse

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
    if existing_users:
        existing_user = existing_users[0]
        # Update custom_metadata with newly provided values
        merged_metadata = dict(existing_user.custom_metadata or {})
        merged_metadata.update(user_in.custom_metadata or {})
        user_in.custom_metadata = merged_metadata
        updated = await repo.update(existing_user.id, user_in)
        return updated
    return await repo.create(user_in)


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
