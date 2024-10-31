from typing import List, Dict, Optional
from datetime import datetime

from core.logging import get_logger
from core.exceptions import ValidationError, ErrorCode, ErrorSeverity
from models.db.extraction import PDFExtraction
from models.db.validation import ValidationResult, ValidationStatus
from models.service.enums import Status
from repositories.validation import validation_repository
from repositories.extraction import extraction_repository

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
        """Validate a single extraction"""
        try:
            logger.info(f"Validating extraction: {extraction.file_name}")
            
            # Basic validation implementation
            result = ValidationResult(
                pdf_extraction_id=extraction.id,
                is_valid=True,
                status=ValidationStatus.VALID,
                details={"message": "Validation not yet implemented"}
            )
            
            # Save validation result
            saved_result = validation_repository.create(result)
            
            # Update extraction status
            extraction.status = Status.VALIDATED
            extraction_repository.update(extraction.id, extraction)
            
            return saved_result
            
        except Exception as e:
            logger.error(f"Validation failed for {extraction.file_name}", exc_info=e)
            raise ValidationError(
                message=f"Validation failed: {str(e)}",
                error_code=ErrorCode.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                details={"file_name": extraction.file_name},
                original_error=e
            )
    
    def validate_all_pending(self) -> List[ValidationResult]:
        """Validate all pending extractions"""
        try:
            # Get pending extractions
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
                error_code=ErrorCode.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR,
                original_error=e
            )

# Create singleton instance
validation_service = ValidationService()
