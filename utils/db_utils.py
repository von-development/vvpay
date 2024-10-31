# utils/db_utils.py
"""Database utilities"""
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timezone
from enum import Enum
import json
from decimal import Decimal
import time
from functools import wraps

from postgrest.exceptions import APIError
from supabase import create_client, Client

from core.config import settings
from core.exceptions import DatabaseError, ErrorCode, ErrorSeverity
from core.logging import get_logger

logger = get_logger(__name__)

def retry_on_error(retries: int = 3, delay: float = 1.0):
    """Retry decorator for database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay} seconds",
                            exc_info=e
                        )
                        time.sleep(delay)
            logger.error(f"All {retries} attempts failed", exc_info=last_error)
            raise last_error
        return wrapper
    return decorator

def serialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize data for database operations"""
    def serialize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        return value

    # Fields to exclude from serialization
    exclude_fields = {'created_at'}
    
    return {
        key: serialize_value(value)
        for key, value in data.items()
        if value is not None and key not in exclude_fields
    }

@retry_on_error()
def init_supabase() -> Client:
    """Initialize Supabase client with error handling and retries"""
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        # Test connection
        client.table("pdf_extractions").select("id").limit(1).execute()
        logger.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.critical("Failed to initialize Supabase client", exc_info=e)
        raise DatabaseError(
            message="Failed to initialize database connection",
            error_code=ErrorCode.DB_CONNECTION,
            severity=ErrorSeverity.CRITICAL,
            original_error=e
        )

# Initialize Supabase client
supabase: Client = init_supabase()

def handle_response(response: Any) -> Union[List[Dict], Dict]:
    """Handle Supabase response with better error handling"""
    try:
        if hasattr(response, 'data'):
            return response.data or []  # Return empty list for no data
        return response or {}  # Return empty dict for no response
    except Exception as e:
        logger.error("Failed to handle database response", exc_info=e)
        return []  # Return safe default

@retry_on_error()
def get_records(
    table_name: str,
    filters: Optional[Dict] = None,
    limit: Optional[int] = None,
    select: str = "*",
    order: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """Get records with enhanced error handling and retries"""
    try:
        logger.debug(
            f"Fetching records from {table_name}",
            extra={
                "filters": filters,
                "limit": limit,
                "select": select,
                "order": order
            }
        )
        
        query = supabase.table(table_name).select(select)
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, Enum):
                    value = value.value
                query = query.eq(key, value)
        
        if order:
            for field, direction in order.items():
                if direction.lower() == 'desc':
                    query = query.order(field, desc=True)
                else:
                    query = query.order(field)
        
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        result = handle_response(response)
        
        logger.info(f"Successfully retrieved {len(result)} records from {table_name}")
        return result
        
    except Exception as e:
        logger.error(
            f"Failed to retrieve records from {table_name}",
            exc_info=e,
            extra={"filters": filters}
        )
        return []  # Return empty list instead of raising error

@retry_on_error()
def insert_record(table_name: str, data: Dict[str, Any]) -> Dict:
    """Insert a single record with retries and better error handling"""
    try:
        logger.debug(
            f"Inserting record into {table_name}",
            extra={
                "table": table_name,
                "data_keys": list(data.keys())
            }
        )
        
        serialized_data = serialize_data(data)
        response = supabase.table(table_name).insert(serialized_data).execute()
        result = handle_response(response)
        
        if isinstance(result, list) and result:
            logger.info(
                f"Successfully inserted record into {table_name}",
                extra={"record_id": result[0].get("id")}
            )
            return result[0]
        
        raise DatabaseError(
            message="Failed to insert record: No result returned",
            details={"table": table_name}
        )
        
    except Exception as e:
        logger.error(
            f"Failed to insert record into {table_name}",
            exc_info=e,
            extra={"table": table_name}
        )
        raise DatabaseError(
            message=f"Failed to insert record: {str(e)}",
            details={"table": table_name},
            original_error=e
        )

def update_record(table_name: str, record_id: str, data: Dict[str, Any]) -> Dict:
    """Update an existing record"""
    try:
        logger.debug(
            f"Updating record in {table_name}",
            extra={
                "table": table_name,
                "record_id": record_id,
                "data_keys": list(data.keys())
            }
        )
        
        # Serialize data
        serialized_data = serialize_data(data)
        
        # Update record
        response = (
            supabase.table(table_name)
            .update(serialized_data)
            .eq("id", record_id)
            .execute()
        )
        result = handle_response(response)
        
        if isinstance(result, list) and result:
            logger.info(
                f"Successfully updated record in {table_name}",
                extra={"record_id": record_id}
            )
            return result[0]
        
        raise DatabaseError(
            message="Failed to update record: No result returned",
            error_code=ErrorCode.DB_ERROR,
            severity=ErrorSeverity.ERROR
        )
        
    except Exception as e:
        logger.error(f"Failed to update record in {table_name}", exc_info=e)
        raise DatabaseError(
            message=f"Failed to update record: {str(e)}",
            error_code=ErrorCode.DB_ERROR,
            severity=ErrorSeverity.ERROR,
            original_error=e
        )

def get_record_by_id(table_name: str, record_id: str) -> Optional[Dict]:
    """Get a single record by ID"""
    try:
        logger.debug(
            f"Fetching record from {table_name}",
            extra={
                "table": table_name,
                "record_id": record_id
            }
        )
        
        response = (
            supabase.table(table_name)
            .select("*")
            .eq("id", record_id)
            .limit(1)
            .execute()
        )
        
        result = handle_response(response)
        
        if isinstance(result, list) and result:
            logger.info(
                f"Successfully retrieved record from {table_name}",
                extra={"record_id": record_id}
            )
            return result[0]
        
        logger.warning(
            f"Record not found in {table_name}",
            extra={"record_id": record_id}
        )
        return None
        
    except Exception as e:
        logger.error(
            f"Failed to retrieve record from {table_name}",
            exc_info=e,
            extra={
                "table": table_name,
                "record_id": record_id
            }
        )
        raise DatabaseError(
            message=f"Failed to retrieve record from {table_name}",
            error_code=ErrorCode.DB_QUERY,
            severity=ErrorSeverity.ERROR,
            details={
                "table": table_name,
                "record_id": record_id
            },
            original_error=e
        )

class DatabaseTransaction:
    """Context manager for database transactions"""
    
    def __init__(self):
        self.operations: List[Dict] = []
        self.rollback_operations: List[Dict] = []
    
    def add_operation(self, operation: Dict, rollback: Dict):
        """Add operation to transaction"""
        self.operations.append(operation)
        self.rollback_operations.append(rollback)
    
    def execute(self):
        """Execute all operations in transaction"""
        results = []
        try:
            for operation in self.operations:
                table = operation["table"]
                action = operation["action"]
                data = operation["data"]
                
                if action == "insert":
                    result = insert_record(table, data)
                elif action == "update":
                    result = update_record(table, data["id"], data)
                else:
                    raise ValueError(f"Unknown action: {action}")
                    
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error("Transaction failed, rolling back", exc_info=e)
            self._rollback()
            raise DatabaseError(
                message="Transaction failed",
                details={"operations_count": len(self.operations)},
                original_error=e
            )
    
    def _rollback(self):
        """Rollback transaction"""
        for operation in reversed(self.rollback_operations):
            try:
                table = operation["table"]
                action = operation["action"]
                data = operation["data"]
                
                if action == "update":
                    update_record(table, data["id"], data)
                elif action == "delete":
                    # Implement delete if needed
                    pass
                    
            except Exception as e:
                logger.error(f"Rollback operation failed: {str(e)}", exc_info=e)

def start_transaction() -> DatabaseTransaction:
    """Start a new database transaction with better error handling"""
    try:
        return DatabaseTransaction()
    except Exception as e:
        logger.error("Failed to start transaction", exc_info=e)
        raise DatabaseError(
            message="Failed to start transaction",
            error_code=ErrorCode.DB_TRANSACTION,
            severity=ErrorSeverity.ERROR,
            original_error=e
        )

def log_processing(
    component: str,
    message: str,
    level: str = "INFO",
    details: Optional[Dict] = None
) -> Dict:
    """Log processing step to database"""
    try:
        data = {
            "component": component,
            "message": message,
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        
        response = supabase.table("processing_logs").insert(data).execute()
        return handle_response(response)[0]
        
    except Exception as e:
        logger.error(f"Failed to log processing: {str(e)}")
        return {}

# Export all functions
__all__ = [
    'get_records',
    'get_record_by_id',
    'insert_record',
    'update_record',
    'handle_response',
    'serialize_data',
    'init_supabase',
    'supabase',
    'start_transaction',
    'log_processing'
]
