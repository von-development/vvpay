"""Repository mixins for extended functionality"""
from typing import Dict, Optional, List
from datetime import datetime, timezone
import logging

from core.exceptions import DatabaseError, ErrorCode, ErrorSeverity
from utils.db_utils import start_transaction

logger = logging.getLogger(__name__)

class TransactionMixin:
    """Mixin for transaction support in repositories"""
    
    def execute_transaction(
        self,
        operations: List[Dict],
        rollback_operations: List[Dict]
    ) -> List[Dict]:
        """Execute a transaction with rollback support"""
        try:
            transaction = start_transaction()
            
            for op, rollback in zip(operations, rollback_operations):
                transaction.add_operation(op, rollback)
                
            return transaction.execute()
            
        except Exception as e:
            logger.error("Transaction failed", exc_info=e)
            raise DatabaseError(
                message="Transaction failed",
                details={
                    "operations_count": len(operations)
                },
                original_error=e
            ) 