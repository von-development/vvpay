"""Core exception handling for the application"""
from typing import Optional, Dict, Any
from enum import Enum

class ErrorSeverity(str, Enum):
    """Enum for error severity levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class ErrorCode(str, Enum):
    """Enum for error codes by category"""
    # Configuration Errors (1xxx)
    CONFIG_ERROR = "1000"
    CONFIG_MISSING = "1001"
    CONFIG_INVALID = "1002"
    INITIALIZATION_ERROR = "1003"
    
    # Database Errors (2xxx)
    DB_ERROR = "2000"
    DB_CONNECTION = "2001"
    DB_QUERY = "2002"
    
    # PDF Processing Errors (3xxx)
    PDF_ERROR = "3000"
    PDF_LOAD = "3001"
    PDF_PARSE = "3002"
    PDF_EXTRACT = "3003"
    
    # Validation Errors (4xxx)
    VALIDATION_ERROR = "4000"
    VALIDATION_SCHEMA = "4001"
    VALIDATION_DATA = "4002"
    
    # Extraction Errors (5xxx)
    EXTRACTION_ERROR = "5000"
    EXTRACTION_FAILED = "5001"
    EXTRACTION_TIMEOUT = "5002"
    
    # API Errors (6xxx)
    API_ERROR = "6000"
    API_REQUEST = "6001"
    API_RESPONSE = "6002"
    API_TIMEOUT = "6003"
    API_AUTH = "6004"

class BaseVPayError(Exception):
    """Base exception class for VPay application"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        severity: ErrorSeverity,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)

class ConfigurationError(BaseVPayError):
    """Raised when there's a configuration error"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFIG_ERROR,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            original_error=original_error
        )

class InitializationError(BaseVPayError):
    """Raised when component initialization fails"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.INITIALIZATION_ERROR,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            original_error=original_error
        )

class DatabaseError(BaseVPayError):
    """Raised when database operations fail"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.DB_ERROR,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_error=original_error
        )

class PDFError(BaseVPayError):
    """Raised when PDF processing fails"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.PDF_ERROR,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_error=original_error
        )

class ExtractionError(BaseVPayError):
    """Raised when data extraction fails"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.EXTRACTION_ERROR,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_error=original_error
        )

class ValidationError(BaseVPayError):
    """Raised when validation fails"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_error=original_error
        )

class APIError(BaseVPayError):
    """Raised when API operations fail"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.API_ERROR,
            severity=ErrorSeverity.ERROR,
            details=details,
            original_error=original_error
        )

# Export all exceptions
__all__ = [
    'ErrorSeverity',
    'ErrorCode',
    'BaseVPayError',
    'ConfigurationError',
    'InitializationError',
    'DatabaseError',
    'PDFError',
    'ExtractionError',
    'ValidationError',
    'APIError'
]