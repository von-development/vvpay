"""Base processing models"""
from typing import TypedDict, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ProcessingState(TypedDict):
    """Base state for processing flows"""
    file_name: str
    content: bytes
    raw_text: Optional[str]
    llm_response: Optional[str]
    structured_data: Optional[Dict]
    error: Optional[str]
    metadata: Optional[Dict]
    timestamp: datetime

class ProcessingResult(BaseModel):
    """Base result for processing operations"""
    success: bool = Field(..., description="Operation success flag")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    duration: float = Field(..., description="Processing duration in seconds") 