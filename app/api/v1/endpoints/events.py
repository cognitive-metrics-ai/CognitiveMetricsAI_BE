from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import EventTransaction, User
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import (
    EventTransactionCreate,
    EventTransactionUpdate,
    EventTransactionResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[EventTransactionResponse],
    summary="List Event Transactions",
    description="Retrieve list of Event_Transactions with event_id, event_name, and event_date.",
)
async def list_event_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    person_id: str = Query(None, description="Filter by person_id"),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(EventTransaction, db)
    filters = {}
    if person_id:
        filters["person_id"] = person_id
    return await repo.get_all(skip=skip, limit=limit, **filters)


@router.post(
    "/",
    response_model=EventTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Event Transaction",
    description="Creates a new Event Transaction record with event_id, event_name, and event_date.",
)
async def create_event_transaction(
    event_in: EventTransactionCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(EventTransaction, db)

    # Check for duplicate event_id
    existing_evt = await repo.get_all(event_id=event_in.event_id)
    if existing_evt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event transaction with event_id '{event_in.event_id}' already exists.",
        )

    # Verify person_id if provided
    if event_in.person_id:
        user_repo = SQLAlchemyRepository(User, db)
        person = await user_repo.get_by_id(event_in.person_id)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person (User) with id '{event_in.person_id}' not found.",
            )

    return await repo.create(event_in)


@router.get(
    "/{event_identifier}",
    response_model=EventTransactionResponse,
    summary="Get Event Transaction Details",
    description="Fetch single event transaction record by UUID or event_id.",
)
async def get_event_transaction(
    event_identifier: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(EventTransaction, db)
    record = await repo.get_by_id(event_identifier)
    if not record:
        by_evt = await repo.get_all(event_id=event_identifier)
        if by_evt:
            return by_evt[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event transaction '{event_identifier}' not found.",
        )
    return record


@router.put(
    "/{event_identifier}",
    response_model=EventTransactionResponse,
    summary="Update Event Transaction",
    description="Update event transaction details.",
)
async def update_event_transaction(
    event_identifier: str,
    event_in: EventTransactionUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(EventTransaction, db)
    record = await repo.get_by_id(event_identifier)
    if not record:
        by_evt = await repo.get_all(event_id=event_identifier)
        if by_evt:
            record = by_evt[0]

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event transaction '{event_identifier}' not found.",
        )

    return await repo.update(record.id, event_in)


@router.delete(
    "/{event_identifier}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Event Transaction",
    description="Deletes an event transaction record.",
)
async def delete_event_transaction(
    event_identifier: str,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyRepository(EventTransaction, db)
    record = await repo.get_by_id(event_identifier)
    if not record:
        by_evt = await repo.get_all(event_id=event_identifier)
        if by_evt:
            record = by_evt[0]

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event transaction '{event_identifier}' not found.",
        )

    await repo.delete(record.id)
    return None
