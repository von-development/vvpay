"""Enumeration types for the application"""
from enum import Enum

class PaymentType(str, Enum):
    """Payment type enumeration"""
    PC = "pc"
    REEMBOLSO = "reembolso"
    BONUS = "bonus"

class Status(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    FAILED = "failed"
    VALIDATED = "validated"

class ValidationStatus(str, Enum):
    """Enhanced validation status tracking"""
    VALID = "valid"                      # Validation passed all checks
    INVALID = "invalid"                  # Failed validation rules
    ALREADY_VALIDATED = "already_validated"  # Document already validated
    FAILED = "failed"                    # System/process failure
    PENDING = "pending"                  # Initial validation state
    PROCESSING = "processing"            # During validation process
    AMOUNT_MISMATCH = "amount_mismatch"  # Specific validation failure
    META_NOT_FOUND = "meta_not_found"    # No matching meta record

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed" 