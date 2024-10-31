"""Core package initialization"""
from .config import Settings, get_settings, BASE_DIR, DATA_DIR
from .exceptions import (
    BaseVPayError, ErrorCode, ErrorSeverity,
    DatabaseError, PDFError, ValidationError,
    APIError, ExtractionError
)
from .logging import get_logger, setup_logging
from .interfaces import (
    ExtractorInterface,
    ProcessorInterface,
    ValidationInterface,
    RepositoryInterface
)

__all__ = [
    # Configuration
    'Settings',
    'get_settings',
    'BASE_DIR',
    'DATA_DIR',
    
    # Exceptions
    'BaseVPayError',
    'ErrorCode',
    'ErrorSeverity',
    'DatabaseError',
    'PDFError',
    'ValidationError',
    'APIError',
    'ExtractionError',
    
    # Interfaces
    'ExtractorInterface',
    'ProcessorInterface',
    'ValidationInterface',
    'RepositoryInterface',
    
    # Logging
    'get_logger',
    'setup_logging'
]
