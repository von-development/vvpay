"""Utility functions package"""
from .db_utils import (
    get_records,
    get_record_by_id,
    insert_record,
    update_record,
    handle_response,
    serialize_data,
    init_supabase,
    supabase,
    start_transaction,
    log_processing
)
from .validators import (
    validate_cnpj,
    validate_date_format,
    validate_amount,
    validate_pix_key
)
from .helpers import (
    format_currency,
    format_date,
    generate_trace_id,
    safe_json_loads
)

__all__ = [
    # Database utilities
    'get_records',
    'get_record_by_id',
    'insert_record',
    'update_record',
    'handle_response',
    'serialize_data',
    'init_supabase',
    'supabase',
    'start_transaction',
    'log_processing',
    
    # Validators
    'validate_cnpj',
    'validate_date_format',
    'validate_amount',
    'validate_pix_key',
    
    # Helpers
    'format_currency',
    'format_date',
    'generate_trace_id',
    'safe_json_loads'
]
