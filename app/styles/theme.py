"""UI style definitions"""
from typing import Dict
from models.service.enums import ValidationStatus, Status

def get_status_style(status: str) -> Dict[str, str]:
    """Get status display style"""
    styles = {
        Status.EXTRACTED: {
            "background-color": "#90EE90",
            "color": "#006400",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        Status.VALIDATED: {
            "background-color": "#87CEEB",
            "color": "#00008B",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        Status.FAILED: {
            "background-color": "#FFB6C1",
            "color": "#8B0000",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        Status.PENDING: {
            "background-color": "#FFE4B5",
            "color": "#8B4513",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        }
    }
    return styles.get(status, {})

def get_validation_style(status: ValidationStatus) -> Dict[str, str]:
    """Get validation status display style"""
    styles = {
        ValidationStatus.VALID: {
            "background-color": "#90EE90",
            "color": "#006400",
            "icon": "✅"
        },
        ValidationStatus.INVALID: {
            "background-color": "#FFB6C1",
            "color": "#8B0000",
            "icon": "❌"
        },
        ValidationStatus.ALREADY_VALIDATED: {
            "background-color": "#FFE4B5",
            "color": "#8B4513",
            "icon": "⚠️"
        },
        ValidationStatus.META_NOT_FOUND: {
            "background-color": "#FFB6C1",
            "color": "#8B0000",
            "icon": "🔍"
        },
        ValidationStatus.AMOUNT_MISMATCH: {
            "background-color": "#FFB6C1",
            "color": "#8B0000",
            "icon": "💰"
        },
        ValidationStatus.PROCESSING: {
            "background-color": "#87CEEB",
            "color": "#00008B",
            "icon": "⏳"
        },
        ValidationStatus.PENDING: {
            "background-color": "#FFE4B5",
            "color": "#8B4513",
            "icon": "⏳"
        }
    }
    return styles.get(status, {
        "background-color": "#E0E0E0",
        "color": "#666666",
        "icon": "❓"
    }) 