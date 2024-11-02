"""Formatting utilities for UI display"""
from typing import List, Dict
from datetime import datetime
from models.service.enums import PaymentType

def format_currency(value: float) -> str:
    """Format currency values"""
    return f"R$ {value:,.2f}"

def format_date(date: datetime, format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
    """Format datetime objects
    
    Args:
        date: The datetime to format
        format_str: The format string to use (default: dd/mm/yyyy HH:MM:SS)
        
    Returns:
        Formatted date string
    """
    if not date:
        return ""
    return date.strftime(format_str)

def format_validation_errors(errors: List[Dict]) -> str:
    """Format validation errors for display"""
    if not errors:
        return ""
    return "\n".join([
        f"• {error['field']}: {error['error']}"
        for error in errors
    ])

def get_payment_type_color(payment_type: str) -> str:
    """Get color for payment type"""
    colors = {
        PaymentType.PC: "blue",
        PaymentType.BONUS: "green",
        PaymentType.REEMBOLSO: "orange"
    }
    return colors.get(payment_type, "gray")

def get_status_color(status: str) -> str:
    """Get color for validation status"""
    colors = {
        "VALID": "green",
        "INVALID": "red",
        "PENDING": "yellow"
    }
    return colors.get(status, "gray")

def format_status(status: str) -> str:
    """Format validation status for display"""
    return f":{get_status_color(status)}[{status}]" 