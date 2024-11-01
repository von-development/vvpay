"""Repository for validation operations"""
from typing import Dict, Optional, List
from datetime import datetime, timezone
from uuid import UUID

from models.db.validation import ValidationResult, ValidationControl
from models.service.enums import PaymentType
from core.exceptions import DatabaseError
from core.logging import get_logger
from utils.db_utils import get_records
from .base import BaseRepository
from .mixins import TransactionMixin

logger = get_logger(__name__)

class ValidationRepository(BaseRepository[ValidationResult], TransactionMixin):
    """Repository for validation operations"""
    
    def __init__(self):
        super().__init__("validation_results", ValidationResult)
        self.validation_control_table = "validation_control"
        logger.info("ValidationRepository initialized")
    
    def get_control(
        self,
        meta_table_id: UUID,
        payment_type: PaymentType,
        competence: str
    ) -> Optional[Dict]:
        """Get validation control entry"""
        try:
            results = get_records(
                self.validation_control_table,
                filters={
                    "meta_table_id": meta_table_id,
                    "payment_type": payment_type,
                    "competence": competence
                }
            )
            return results[0] if results else None
            
        except Exception as e:
            logger.error("Failed to get validation control", exc_info=e)
            raise DatabaseError(
                message="Failed to get validation control",
                details={
                    "meta_table_id": str(meta_table_id),
                    "payment_type": payment_type,
                    "competence": competence
                },
                original_error=e
            )
    
    def create_control(self, control: ValidationControl) -> Dict:
        """Create validation control entry"""
        try:
            # Convert model to dict and ensure validated_at
            data = control.model_dump(exclude={'id'})
            if 'validated_at' not in data:
                data['validated_at'] = datetime.now(timezone.utc)
            
            # Define operations
            operations = [{
                "table": self.validation_control_table,
                "action": "insert",
                "data": data
            }]
            
            rollback_operations = [{
                "table": self.validation_control_table,
                "action": "delete",
                "data": {"id": None}
            }]
            
            # Execute transaction
            results = self.execute_transaction(operations, rollback_operations)
            result = results[0] if results else None
            
            if not result:
                raise DatabaseError(
                    message="Failed to create validation control",
                    details={
                        "meta_table_id": str(control.meta_table_id),
                        "competence": control.competence
                    }
                )
            
            logger.info(
                "Validation control created successfully",
                extra={"record_id": result.get("id")}
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to create validation control", exc_info=e)
            raise DatabaseError(
                message="Failed to create validation control",
                details={
                    "meta_table_id": str(control.meta_table_id),
                    "competence": control.competence
                },
                original_error=e
            )

    def get_validation_history(
        self,
        limit: int = 20
    ) -> List[Dict]:
        """Get validation history with proper ordering"""
        try:
            return get_records(
                self.table_name,
                order={
                    "field": "validated_at",
                    "direction": "desc"
                },
                limit=limit
            )
        except Exception as e:
            logger.error("Failed to get validation history", exc_info=e)
            return []

# Create singleton instance
validation_repository = ValidationRepository() 