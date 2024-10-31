"""Validation utilities"""
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from core.exceptions import ValidationError, ErrorCode, ErrorSeverity

def validate_cnpj(cnpj: str) -> str:
    """Validate CNPJ format and digits"""
    # Remove non-digits
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        raise ValidationError(
            message="CNPJ must have 14 digits",
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
    
    return cnpj

def validate_date_format(date_str: str, format: str = "%m/%Y") -> str:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, format)
        return date_str
    except ValueError as e:
        raise ValidationError(
            message=f"Invalid date format. Expected {format}",
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            original_error=e
        )

def validate_amount(
    amount: Union[str, float, Decimal],
    min_value: float = 0.0
) -> Decimal:
    """Validate and convert amount"""
    try:
        if isinstance(amount, str):
            # Remove currency symbol and convert commas
            amount = amount.replace('R$', '').replace('.', '').replace(',', '.')
        
        amount_decimal = Decimal(str(amount))
        
        if amount_decimal <= min_value:
            raise ValidationError(
                message=f"Amount must be greater than {min_value}",
                error_code=ErrorCode.VALIDATION_ERROR,
                severity=ErrorSeverity.ERROR
            )
            
        return amount_decimal
        
    except (ValueError, InvalidOperation) as e:
        raise ValidationError(
            message="Invalid amount format",
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            original_error=e
        )

def validate_pix_key(pix_key: str) -> str:
    """Validate PIX key format"""
    # Add PIX key validation logic
    if not pix_key:
        raise ValidationError(
            message="PIX key cannot be empty",
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR
        )
    return pix_key