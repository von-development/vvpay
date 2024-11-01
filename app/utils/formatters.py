"""Formatting utilities for UI display"""
from typing import List, Dict
from models.service.enums import PaymentType, ValidationStatus
from datetime import datetime

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

def get_validation_status_display(status: ValidationStatus) -> Dict[str, str]:
    """Get display properties for validation status"""
    status_config = {
        ValidationStatus.VALID: {
            "color": "success",
            "icon": "✅",
            "label": "Valid"
        },
        ValidationStatus.INVALID: {
            "color": "error",
            "icon": "❌",
            "label": "Invalid"
        },
        ValidationStatus.ALREADY_VALIDATED: {
            "color": "warning",
            "icon": "⚠️",
            "label": "Already Validated"
        },
        ValidationStatus.META_NOT_FOUND: {
            "color": "error",
            "icon": "🔍",
            "label": "No Meta Record"
        },
        ValidationStatus.AMOUNT_MISMATCH: {
            "color": "error",
            "icon": "💰",
            "label": "Amount Mismatch"
        },
        ValidationStatus.PROCESSING: {
            "color": "info",
            "icon": "⏳",
            "label": "Processing"
        },
        ValidationStatus.PENDING: {
            "color": "warning",
            "icon": "⏳",
            "label": "Pending"
        }
    }
    return status_config.get(status, {
        "color": "default",
        "icon": "❓",
        "label": str(status)
    })

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        if isinstance(dt_str, str):
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_str
    return dt_str 