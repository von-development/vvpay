from typing import List, Dict, Optional
from datetime import datetime, timezone
import re

from core.logging import get_logger
from core.exceptions import ValidationError
from models.db.extraction import PDFExtraction
from models.db.validation import ValidationResult, ValidationControl, ValidationStatus
from models.service.enums import Status, PaymentType
from repositories.validation import validation_repository
from repositories.extraction import extraction_repository
from repositories.meta import meta_repository

logger = get_logger(__name__)

class ValidationService:
    """Service for validating extracted data"""
    
    def __init__(self):
        logger.info("Initializing ValidationService")
    
    def check_validation_control(self, extraction: PDFExtraction) -> bool:
        """Check validation control rules"""
        try:
            # Check if already validated
            existing_validations = validation_repository.get_all(
                filters={"pdf_extraction_id": extraction.id}
            )
            if existing_validations:
                logger.warning(f"Document {extraction.file_name} already validated")
                return False
            
            # Check meta table
            meta_records = meta_repository.get_all(
                filters={"cpf_cnpj": extraction.cnpj}
            )
            if not meta_records:
                logger.warning(f"No meta record found for CNPJ {extraction.cnpj}")
                return False
            
            # Check validation control
            meta_record = meta_records[0]
            existing_control = validation_repository.get_control(
                meta_table_id=meta_record.id,
                payment_type=extraction.payment_type,
                competence=extraction.competence
            )
            
            if existing_control:
                logger.warning(
                    f"Validation control already exists for {extraction.competence}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error("Validation control check failed", exc_info=e)
            return False
    
    def validate_extraction(
        self,
        extraction: PDFExtraction,
        metadata: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate a single extraction"""
        validation_timestamp = datetime.now(timezone.utc)
        try:
            logger.info(f"Validating extraction: {extraction.file_name}")
            
            # Get meta table record
            meta_records = meta_repository.get_all(
                filters={"cpf_cnpj": extraction.cnpj}
            )
            
            if not meta_records:
                return ValidationResult(
                    pdf_extraction_id=extraction.id,
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    validation_errors=[{
                        "field": "cnpj",
                        "error": "CNPJ not found in meta table"
                    }],
                    validated_at=validation_timestamp
                )
            
            meta_record = meta_records[0]
            validation_errors = []
            
            # Compare values based on payment type
            if extraction.payment_type == PaymentType.PC and meta_record.ago_pc:
                if meta_record.ago_pc != extraction.valor:
                    validation_errors.append({
                        "field": "valor",
                        "error": f"Amount mismatch for PC: expected {meta_record.ago_pc}"
                    })
            elif extraction.payment_type == PaymentType.BONUS and meta_record.ago_bn:
                if meta_record.ago_bn != extraction.valor:
                    validation_errors.append({
                        "field": "valor",
                        "error": f"Amount mismatch for Bonus: expected {meta_record.ago_bn}"
                    })
            elif extraction.payment_type == PaymentType.REEMBOLSO and meta_record.ago_re:
                if meta_record.ago_re != extraction.valor:
                    validation_errors.append({
                        "field": "valor",
                        "error": f"Amount mismatch for Reembolso: expected {meta_record.ago_re}"
                    })
            
            # Check if already validated for this period
            existing_control = validation_repository.get_control(
                meta_table_id=meta_record.id,
                payment_type=extraction.payment_type,
                competence=extraction.competence
            )
            
            if existing_control:
                return ValidationResult(
                    pdf_extraction_id=extraction.id,
                    meta_table_id=meta_record.id,
                    is_valid=False,
                    status=ValidationStatus.ALREADY_VALIDATED,
                    validation_errors=[{
                        "field": "control",
                        "error": "Document already validated for this period"
                    }],
                    validated_at=validation_timestamp
                )
            
            # Create validation result
            result = ValidationResult(
                pdf_extraction_id=extraction.id,
                meta_table_id=meta_record.id,
                is_valid=len(validation_errors) == 0,
                status=ValidationStatus.VALID if len(validation_errors) == 0 else ValidationStatus.INVALID,
                validation_errors=validation_errors,
                details={
                    "file_name": extraction.file_name,
                    "meta_table": meta_record.model_dump()
                },
                validated_at=validation_timestamp
            )
            
            # Save validation result
            saved_result = validation_repository.create(result)
            
            # If valid, create validation control entry
            if result.is_valid:
                control = ValidationControl(
                    meta_table_id=meta_record.id,
                    payment_type=extraction.payment_type,
                    competence=extraction.competence,
                    validated_at=validation_timestamp
                )
                validation_repository.create_control(control)
                
                # Update extraction status
                extraction.status = Status.VALIDATED
                extraction_repository.update(extraction.id, extraction)
            else:
                extraction.status = Status.FAILED
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
                details={"error": str(e)},
                original_error=e
            )

# Create singleton instance
validation_service = ValidationService()
