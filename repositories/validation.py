"""Repository for validation operations"""
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timezone
from uuid import UUID

from models.db.validation import ValidationResult, ValidationControl
from models.service.enums import PaymentType, ValidationStatus
from core.exceptions import DatabaseError
from core.logging import get_logger
from utils.db_utils import get_records, start_transaction
from .base import BaseRepository
from .mixins import TransactionMixin

logger = get_logger(__name__)

class ValidationRepository(BaseRepository[ValidationResult], TransactionMixin):
    """Repository for validation operations"""
    
    def __init__(self):
        super().__init__("validation_results", ValidationResult)
        self.validation_control_table = "validation_control"
        logger.info("ValidationRepository initialized")
    
    def get_validation_history(
        self,
        pdf_extraction_id: UUID,
        include_details: bool = True
    ) -> List[ValidationResult]:
        """Get all validation attempts for a document"""
        try:
            results = get_records(
                self.table_name,
                filters={"pdf_extraction_id": pdf_extraction_id},
                order={"field": "validated_at", "direction": "desc"}
            )
            return [self.model_class(**result) for result in results]
        except Exception as e:
            logger.error("Failed to get validation history", exc_info=e)
            return []

    def check_control_exists(
        self,
        meta_table_id: UUID,
        payment_type: PaymentType,
        competence: str
    ) -> Optional[ValidationControl]:
        """Check if validation control exists"""
        try:
            results = get_records(
                self.validation_control_table,
                filters={
                    "meta_table_id": meta_table_id,
                    "payment_type": payment_type,
                    "competence": competence
                }
            )
            return ValidationControl(**results[0]) if results else None
        except Exception as e:
            logger.error("Failed to check validation control", exc_info=e)
            return None

    def create_with_control(
        self,
        result: ValidationResult,
        control: Optional[ValidationControl] = None
    ) -> Tuple[ValidationResult, Optional[ValidationControl]]:
        """Create validation result and optionally create control in transaction"""
        try:
            transaction = start_transaction()
            
            # Add validation result operation
            transaction.add_operation(
                {
                    "table": self.table_name,
                    "action": "insert",
                    "data": result.model_dump(exclude={'id'})
                },
                {
                    "table": self.table_name,
                    "action": "delete",
                    "data": {"id": None}
                }
            )
            
            # Add control operation if provided
            if control and result.is_valid:
                transaction.add_operation(
                    {
                        "table": self.validation_control_table,
                        "action": "insert",
                        "data": control.model_dump(exclude={'id'})
                    },
                    {
                        "table": self.validation_control_table,
                        "action": "delete",
                        "data": {"id": None}
                    }
                )
            
            # Execute transaction
            results = transaction.execute()
            
            saved_result = self.model_class(**results[0])
            saved_control = ValidationControl(**results[1]) if len(results) > 1 else None
            
            return saved_result, saved_control
            
        except Exception as e:
            logger.error("Failed to create validation with control", exc_info=e)
            raise DatabaseError(
                message="Failed to create validation with control",
                details={
                    "pdf_extraction_id": str(result.pdf_extraction_id)
                },
                original_error=e
            )

# Create singleton instance
validation_repository = ValidationRepository() 