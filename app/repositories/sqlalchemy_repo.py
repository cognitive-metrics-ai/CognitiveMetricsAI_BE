from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository(BaseRepository[ModelType], Generic[ModelType]):
    """Standard Async SQLAlchemy implementation of the BaseRepository.
    
    Provides ready-to-use CRUD operations for any SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.unique().scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def create(self, obj_in: Any) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        elif hasattr(obj_in, "model_dump"):
            db_obj = self.model(**obj_in.model_dump())
        else:
            db_obj = self.model(**obj_in.__dict__)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: Any, obj_in: Any) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True
