"""Payment repository"""
from models.db.payment import PaymentRecord
from .base import BaseRepository

class PaymentRepository(BaseRepository[PaymentRecord]):
    def __init__(self):
        super().__init__("payment_records", PaymentRecord)

payment_repository = PaymentRepository() 