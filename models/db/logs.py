"""Processing logs model"""
from typing import Optional, Dict
from pydantic import Field, field_validator
from datetime import datetime, timezone

from .base import DBModelBase

class ProcessingLog(DBModelBase):
    """
    Processing and audit logs.
    Maps to 'processing_logs' in database.
    """
    component: str = Field(..., description="Component name", index=True)
    message: str = Field(..., description="Log message")
    level: str = Field(..., description="Log level", index=True)
    details: Dict = Field(default_factory=dict, description="Additional log details")
    trace_id: Optional[str] = Field(default=None, description="Trace ID for request tracking")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Log timestamp",
        index=True
    )