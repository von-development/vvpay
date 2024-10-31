"""Payment record model"""
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from pydantic import Field

from .base import DBModelBase
from ..service.enums import PaymentStatus

class PaymentRecord(DBModelBase):
    """
    Payment transaction records.
    Maps to 'payment_records' in database.
    """
    validation_id: UUID = Field(..., description="Reference to validation result", index=True)
    pix_key: str = Field(..., description="PIX key for payment")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    scheduled_for: datetime = Field(..., description="Scheduled payment date")
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="Payment status",
        index=True
    )
    transaction_id: Optional[str] = Field(default=None, description="Bank transaction ID")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    executed_at: Optional[datetime] = Field(default=None, description="Execution timestamp")