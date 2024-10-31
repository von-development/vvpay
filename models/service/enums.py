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
    """Validation status enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    ALREADY_VALIDATED = "already_validated"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed" 