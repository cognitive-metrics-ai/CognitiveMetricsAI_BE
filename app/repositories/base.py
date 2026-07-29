from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract Base Repository defining the contract for data persistence operations.
    
    Businesses can implement custom subclasses of this repository interface to connect
    to enterprise data sources (e.g. legacy SQL databases, REST APIs, or custom database schemas)
    without modifying API endpoints or frontend logic.
    """

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Fetch a single entity by primary key / ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Fetch multiple entities with pagination and optional filtering."""
        pass

    @abstractmethod
    async def create(self, obj_in: Any) -> T:
        """Create and persist a new entity."""
        pass

    @abstractmethod
    async def update(self, id: Any, obj_in: Any) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete or soft-delete an entity."""
        pass
