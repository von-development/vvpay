"""Logs repository"""
from models.db.logs import ProcessingLog
from .base import BaseRepository

class LogRepository(BaseRepository[ProcessingLog]):
    def __init__(self):
        super().__init__("processing_logs", ProcessingLog)

log_repository = LogRepository() 