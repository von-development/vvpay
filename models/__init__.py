"""
Models package initialization.

This module organizes all models into logical groups:
1. Database Models (db) - Match Supabase schema
2. Service Models (service) - Business logic and enums
3. Processing Models (processing) - LLM and workflow states
"""

# Database Models
from .db.base import DBModelBase
from .db.meta import MetaTable
from .db.extraction import PDFExtraction
from .db.validation import ValidationResult, ValidationControl, ValidationError
from .db.payment import PaymentRecord
from .db.logs import ProcessingLog

# Service Models
from .service.enums import (
    PaymentType,
    Status,
    ValidationStatus,
    PaymentStatus
)

# Processing Models
from .processing.states import GraphState, create_initial_state
from .processing.llm import InvoiceData

__all__ = [
    # Database Models
    'DBModelBase',
    'MetaTable',
    'PDFExtraction',
    'ValidationResult',
    'ValidationControl',
    'ValidationError',
    'PaymentRecord',
    'ProcessingLog',
    
    # Service Models
    'PaymentType',
    'Status',
    'ValidationStatus',
    'PaymentStatus',
    
    # Processing Models
    'GraphState',
    'create_initial_state',
    'InvoiceData'
]
