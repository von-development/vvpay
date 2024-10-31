"""Base database model"""
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

class DBModelBase(BaseModel):
    """Base model for database entities"""
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Primary key"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )