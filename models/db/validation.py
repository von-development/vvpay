"""Validation database models"""
from typing import Optional, List, Dict
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field

from .base import DBModelBase
from ..service.enums import ValidationStatus, PaymentType

class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field with error")
    error: str = Field(..., description="Error description")
    severity: str = Field(default="error", description="Error severity")
    details: dict = Field(default_factory=dict, description="Additional error details")

class ValidationResult(DBModelBase):
    """Database model for validation results"""
    pdf_extraction_id: UUID = Field(..., description="Reference to extraction")
    meta_table_id: Optional[UUID] = Field(default=None, description="Reference to meta_table")
    is_valid: bool = Field(..., description="Validation result flag")
    status: ValidationStatus = Field(..., description="Validation status")
    validation_errors: List[ValidationError] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    details: dict = Field(default_factory=dict, description="Additional validation details")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Validation timestamp"
    )

class ValidationControl(DBModelBase):
    """Database model for validation control"""
    meta_table_id: UUID = Field(..., description="Reference to meta_table")
    payment_type: PaymentType = Field(..., description="Payment type")
    competence: str = Field(..., description="Competence period")
    validated_at: datetime = Field(..., description="Validation timestamp")

    class Config:
        """Model configuration"""
        unique_together = [('meta_table_id', 'payment_type', 'competence')]