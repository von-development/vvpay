"""PDF extraction model"""
from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import Field, field_validator
import re

from .base import DBModelBase
from ..service.enums import Status, PaymentType

class PDFExtraction(DBModelBase):
    """
    PDF extraction results.
    Maps to 'pdf_extractions' in database.
    """
    file_name: str = Field(..., description="Original file name")
    raw_text: str = Field(..., description="Extracted text content")
    cnpj: str = Field(..., description="CNPJ number", index=True)
    valor: Decimal = Field(..., gt=0, description="Payment amount")
    competence: str = Field(default="", description="Payment period", index=True)
    payee_name: str = Field(..., description="Provider name")
    description: str = Field(default="", description="Service description")
    payment_type: PaymentType = Field(default=PaymentType.PC, description="Payment type", index=True)
    status: Status = Field(default=Status.PENDING, description="Processing status", index=True)
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Extraction confidence")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Extraction timestamp"
    )

    @field_validator('competence')
    @classmethod
    def validate_competence(cls, v: str) -> str:
        """Validate competence format (MM/YYYY)"""
        if not re.match(r'^\d{2}/\d{4}$', v):
            raise ValueError("Competence must be in MM/YYYY format")
        return v

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Validate CNPJ format (14 digits)"""
        cnpj = re.sub(r'[^0-9]', '', v)
        if len(cnpj) != 14:
            raise ValueError("CNPJ must have exactly 14 digits")
        return cnpj 