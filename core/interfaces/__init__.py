"""Interface package initialization"""
from typing import TypeVar, Generic

from .base import BaseInterface
from .repository import RepositoryInterface
from .service import (
    ExtractorInterface,
    ProcessorInterface,
    ValidationInterface
)

T = TypeVar('T')

__all__ = [
    'BaseInterface',
    'RepositoryInterface',
    'ExtractorInterface',
    'ProcessorInterface',
    'ValidationInterface',
    'T'
] 