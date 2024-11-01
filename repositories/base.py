"""Base repository implementation"""
from typing import Optional, Dict, List, TypeVar, Generic, Type
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from core.exceptions import DatabaseError
from core.logging import get_logger
from utils.db_utils import get_records, get_record_by_id, insert_record, update_record

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class
        self.logger = get_logger(f"repositories.{table_name}")
        self.logger.info(f"Initialized repository for {table_name}")
    
    def get_by_id(self, record_id: UUID) -> Optional[T]:
        """Get a record by ID"""
        try:
            result = get_record_by_id(self.table_name, record_id)
            return self.model_class(**result) if result else None
        except Exception as e:
            self.logger.error(f"Failed to fetch record", exc_info=e)
            raise DatabaseError(
                message=f"Failed to fetch {self.table_name} record",
                details={"record_id": str(record_id)},
                original_error=e
            )
    
    def get_all(
        self,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        order: Optional[Dict[str, Dict[str, str]]] = None
    ) -> List[T]:
        """Get all records matching filters"""
        try:
            results = get_records(
                self.table_name,
                filters=filters,
                limit=limit,
                order=order
            )
            return [self.model_class(**record) for record in results]
        except Exception as e:
            self.logger.error("Failed to fetch records", exc_info=e)
            raise DatabaseError(
                message=f"Failed to fetch {self.table_name} records",
                details={"error": str(e)},
                original_error=e
            )
    
    def create(self, model: T) -> T:
        """Create a new record"""
        try:
            data = model.model_dump(exclude={'id'})
            result = insert_record(self.table_name, data)
            return self.model_class(**result)
        except Exception as e:
            self.logger.error("Failed to create record", exc_info=e)
            raise DatabaseError(
                message=f"Failed to create {self.table_name} record",
                details={"error": str(e)},
                original_error=e
            )
    
    def update(self, record_id: UUID, model: T) -> T:
        """Update an existing record"""
        try:
            data = model.model_dump(exclude={'id'})
            result = update_record(self.table_name, record_id, data)
            return self.model_class(**result)
        except Exception as e:
            self.logger.error("Failed to update record", exc_info=e)
            raise DatabaseError(
                message=f"Failed to update {self.table_name} record",
                details={"record_id": str(record_id)},
                original_error=e
            )