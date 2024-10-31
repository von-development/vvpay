"""Formatting utilities for UI display"""
from typing import List, Dict
from models.service.enums import PaymentType

def format_currency(value: float) -> str:
    """Format currency values"""
    return f"R$ {value:,.2f}"

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