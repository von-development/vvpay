"""Repository layer interfaces"""
from abc import abstractmethod
from typing import Optional, List, Dict, TypeVar, Generic
from uuid import UUID

from .base import BaseInterface
from models.db.base import DBModelBase

T = TypeVar('T', bound=DBModelBase)

class RepositoryInterface(BaseInterface, Generic[T]):
    """Base interface for repositories"""
    @abstractmethod
    def get_by_id(self, record_id: UUID) -> Optional[T]:
        """Get a record by ID"""
        pass

    @abstractmethod
    def get_all(
        self,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[T]:
        """Get all records matching filters"""
        pass

    @abstractmethod
    def create(self, data: T) -> T:
        """Create a new record"""
        pass

    @abstractmethod
    def update(self, record_id: UUID, data: T) -> T:
        """Update an existing record"""
        pass 