"""UI style definitions"""
from typing import Dict

VALIDATION_COLORS = {
    "VALID": "#28a745",    # Green
    "INVALID": "#dc3545",  # Red
    "PENDING": "#ffc107",  # Yellow
    "DEFAULT": "#6c757d"   # Gray
}

def get_status_style(status: str) -> Dict[str, str]:
    """Get status display style"""
    return {
        "extracted": {
            "background-color": "#90EE90",
            "color": "#006400",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        "validated": {
            "background-color": "#87CEEB",
            "color": "#00008B",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        "failed": {
            "background-color": "#FFB6C1",
            "color": "#8B0000",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        },
        "pending": {
            "background-color": "#FFE4B5",
            "color": "#8B4513",
            "padding": "4px 8px",
            "border-radius": "4px",
            "font-weight": "bold"
        }
    }.get(status, {}) 