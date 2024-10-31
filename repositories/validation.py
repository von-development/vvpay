"""Validation repository"""
from models.db.validation import ValidationResult
from .base import BaseRepository

class ValidationRepository(BaseRepository[ValidationResult]):
    """Repository for validation results"""
    def __init__(self):
        super().__init__("validation_results", ValidationResult)

validation_repository = ValidationRepository() 