"""Repository mixins for extended functionality"""
from typing import Dict, Optional, List
from datetime import datetime, timezone

from core.exceptions import DatabaseError, ErrorCode, ErrorSeverity
from utils.db_utils import start_transaction

class TransactionMixin:
    """Mixin for transaction support in repositories"""
    
    def execute_transaction(
        self,
        operations: List[Dict],
        rollback_operations: List[Dict]
    ) -> List[Dict]:
        """Execute a transaction with rollback support"""
        transaction = start_transaction()
        
        for op, rollback in zip(operations, rollback_operations):
            transaction.add_operation(op, rollback)
            
        return transaction.execute() 