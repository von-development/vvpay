from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from uuid import UUID

from core.logging import get_logger
from core.exceptions import ValidationError
from models.db.extraction import PDFExtraction
from models.db.validation import ValidationResult, ValidationControl
from models.service.enums import Status, PaymentType, ValidationStatus
from repositories.validation import validation_repository
from repositories.extraction import extraction_repository
from repositories.meta import meta_repository

logger = get_logger(__name__)

class ValidationService:
    """Service for validating extracted data"""
    
    def __init__(self):
        logger.info("Initializing ValidationService")
    
    def validate_extraction(
        self,
        extraction: PDFExtraction,
        metadata: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate a single extraction with improved tracking"""
        validation_timestamp = datetime.now(timezone.utc)
        
        try:
            logger.info(f"Validating extraction: {extraction.file_name}")
            
            # Initial validation result with pending status
            result = ValidationResult(
                pdf_extraction_id=extraction.id,
                is_valid=False,
                status=ValidationStatus.PROCESSING,
                validated_at=validation_timestamp,
                details={"file_name": extraction.file_name}
            )
            
            # Get meta table record
            meta_records = meta_repository.get_all(
                filters={"cpf_cnpj": extraction.cnpj}
            )
            
            if not meta_records:
                result.status = ValidationStatus.META_NOT_FOUND
                result.validation_errors.append({
                    "field": "cnpj",
                    "error": "CNPJ not found in meta table"
                })
                return validation_repository.create(result)
            
            meta_record = meta_records[0]
            result.meta_table_id = meta_record.id
            
            # Check existing validation control
            existing_control = validation_repository.check_control_exists(
                meta_table_id=meta_record.id,
                payment_type=extraction.payment_type,
                competence=extraction.competence
            )
            
            if existing_control:
                result.status = ValidationStatus.ALREADY_VALIDATED
                result.validation_errors.append({
                    "field": "control",
                    "error": "Document already validated for this period"
                })
                return validation_repository.create(result)
            
            # Validate amount based on payment type
            validation_errors = []
            if extraction.payment_type == PaymentType.PC and meta_record.ago_pc:
                if meta_record.ago_pc != extraction.valor:
                    validation_errors.append({
                        "field": "valor",
                        "error": f"Amount mismatch for PC: expected {meta_record.ago_pc}"
                    })
            # Add similar checks for other payment types...
            
            # Update validation result
            result.is_valid = len(validation_errors) == 0
            result.status = ValidationStatus.VALID if result.is_valid else ValidationStatus.AMOUNT_MISMATCH
            result.validation_errors = validation_errors
            result.details.update({
                "meta_table": meta_record.model_dump()
            })
            
            # Create control if valid
            control = None
            if result.is_valid:
                control = ValidationControl(
                    meta_table_id=meta_record.id,
                    payment_type=extraction.payment_type,
                    competence=extraction.competence,
                    validated_at=validation_timestamp
                )
            
            # Save result and control in transaction
            saved_result, saved_control = validation_repository.create_with_control(result, control)
            
            # Update extraction status
            extraction.status = Status.VALIDATED if result.is_valid else Status.FAILED
            extraction_repository.update(extraction.id, extraction)
            
            return saved_result
            
        except Exception as e:
            logger.error(f"Validation failed for {extraction.file_name}", exc_info=e)
            raise ValidationError(
                message=f"Validation failed: {str(e)}",
                details={"file_name": extraction.file_name},
                original_error=e
            )
    
    def validate_all_pending(self) -> List[ValidationResult]:
        """Validate all pending extractions"""
        try:
            pending = extraction_repository.get_all(
                filters={"status": Status.EXTRACTED}
            )
            
            results = []
            for extraction in pending:
                try:
                    result = self.validate_extraction(extraction)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate {extraction.file_name}", exc_info=e)
            
            return results
            
        except Exception as e:
            logger.error("Failed to validate pending extractions", exc_info=e)
            raise ValidationError(
                message="Failed to validate pending extractions",
                details={"error": str(e)},
                original_error=e
            )

# Create singleton instance
validation_service = ValidationService()
