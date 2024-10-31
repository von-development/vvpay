"""Helper utilities"""
import json
from typing import Any, Optional
from datetime import datetime
import uuid
from decimal import Decimal

from core.logging import get_logger

logger = get_logger(__name__)

def format_currency(value: Decimal) -> str:
    """Format currency values"""
    return f"R$ {value:,.2f}"

def format_date(
    date: datetime,
    format: str = "%d/%m/%Y %H:%M:%S"
) -> str:
    """Format datetime objects"""
    return date.strftime(format)

def generate_trace_id() -> str:
    """Generate unique trace ID"""
    return str(uuid.uuid4())

def safe_json_loads(data: str) -> Optional[Any]:
    """Safely parse JSON string"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        return None 