"""Repository for PDF extractions"""
from typing import Dict, Optional
from datetime import datetime, timezone

from models.db.extraction import PDFExtraction
from models.service.enums import Status
from core.exceptions import DatabaseError
from core.logging import get_logger
from .base import BaseRepository
from .mixins import TransactionMixin

logger = get_logger(__name__)

class ExtractionRepository(BaseRepository[PDFExtraction], TransactionMixin):
    """Repository for PDF extractions"""
    
    def __init__(self):
        super().__init__("pdf_extractions", PDFExtraction)
        logger.info("ExtractionRepository initialized")
    
    def create_extraction(self, extraction: PDFExtraction) -> Dict:
        """Create extraction with transaction support"""
        try:
            # Validate input type
            if not isinstance(extraction, PDFExtraction):
                raise DatabaseError(
                    message=f"Expected PDFExtraction model, got {type(extraction)}",
                    details={"model_type": str(type(extraction))}
                )
            
            # Convert model to dict and exclude unnecessary fields
            data = extraction.model_dump(
                exclude={'id', 'created_at'},  # Explicitly exclude fields
                exclude_unset=True
            )
            
            # Define operations
            operations = [{
                "table": self.table_name,
                "action": "insert",
                "data": data
            }]
            
            rollback_operations = [{
                "table": self.table_name,
                "action": "delete",
                "data": {"id": None}
            }]
            
            # Execute transaction
            results = self.execute_transaction(operations, rollback_operations)
            result = results[0] if results else None
            
            if not result:
                raise DatabaseError(
                    message="Failed to create extraction record",
                    details={"doc_name": extraction.file_name}
                )
            
            logger.info(
                "Extraction record created successfully",
                extra={"record_id": result.get("id")}
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to create extraction record",
                exc_info=e,
                extra={"doc_name": extraction.file_name}
            )
            raise DatabaseError(
                message="Failed to create extraction record",
                details={"doc_name": extraction.file_name},
                original_error=e
            )

# Create singleton instance
extraction_repository = ExtractionRepository()