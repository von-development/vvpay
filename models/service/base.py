"""Base service models"""
from typing import Optional, Dict, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

T = TypeVar('T')

class ServiceResult(BaseModel, Generic[T]):
    """Generic result for service operations"""
    success: bool = Field(..., description="Operation success flag")
    data: Optional[T] = Field(default=None, description="Operation result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    trace_id: Optional[str] = Field(default=None, description="Operation trace ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

class ServiceContext(BaseModel):
    """Context for service operations"""
    user_id: Optional[UUID] = Field(default=None, description="User ID")
    trace_id: Optional[str] = Field(default=None, description="Trace ID")
    metadata: Dict = Field(default_factory=dict, description="Operation metadata")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Operation start time") 