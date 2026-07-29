from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import PerformanceReview
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import ReviewCreate, ReviewResponse

router = APIRouter()


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Performance Review",
    description="""
Create or submit a performance review record for an employee.
Supports custom metadata for storing business-specific evaluation rubric scores or external HR system references.
""",
)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(PerformanceReview, db)
    return await repo.create(review_in)


@router.get(
    "/",
    response_model=List[ReviewResponse],
    summary="List Performance Reviews",
    description="""
Retrieve performance reviews with optional filtering by employee, reviewer, period, or status.
""",
)
async def list_reviews(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination max limit"),
    employee_id: Optional[str] = Query(None, description="Filter reviews by employee UUID"),
    reviewer_id: Optional[str] = Query(None, description="Filter reviews by reviewer UUID"),
    period: Optional[str] = Query(None, description="Filter by review period e.g. Q1 2026"),
    review_status: Optional[str] = Query(None, alias="status", description="Filter by status (draft, submitted, approved)"),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(PerformanceReview, db)
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if reviewer_id:
        filters["reviewer_id"] = reviewer_id
    if period:
        filters["period"] = period
    if review_status:
        filters["status"] = review_status
    return await repo.get_all(skip=skip, limit=limit, **filters)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Get Performance Review Details",
    description="Retrieve details and evaluation feedback for a specific performance review.",
)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(PerformanceReview, db)
    review = await repo.get_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance Review with ID '{review_id}' not found.",
        )
    return review
