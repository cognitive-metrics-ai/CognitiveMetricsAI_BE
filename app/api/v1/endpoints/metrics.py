from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Metric
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import MetricCreate, MetricResponse

router = APIRouter()


@router.post(
    "/",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Cognitive & Performance Metric",
    description="""
Record a cognitive or productivity metric entry for an employee.
Examples of metric types include:
- `problem_solving` (Cognitive)
- `velocity` (Productivity)
- `focus_score` (Cognitive)
- `code_review_thoroughness` (Quality)

Businesses can attach any custom enterprise payload data inside `custom_metadata`.
""",
)
async def create_metric(
    metric_in: MetricCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Metric, db)
    return await repo.create(metric_in)


@router.get(
    "/",
    response_model=List[MetricResponse],
    summary="Query Cognitive Metrics",
    description="""
Retrieve performance metrics with optional filtering by employee ID, metric type, or category.
""",
)
async def list_metrics(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination max limit"),
    employee_id: Optional[str] = Query(None, description="Filter metrics by employee UUID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type (e.g. problem_solving)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Cognitive, Productivity)"),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Metric, db)
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if metric_type:
        filters["metric_type"] = metric_type
    if category:
        filters["category"] = category
    return await repo.get_all(skip=skip, limit=limit, **filters)


@router.get(
    "/{metric_id}",
    response_model=MetricResponse,
    summary="Get Metric Details",
    description="Retrieve details for a single recorded metric entry.",
)
async def get_metric(
    metric_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(Metric, db)
    metric = await repo.get_by_id(metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with ID '{metric_id}' not found.",
        )
    return metric
