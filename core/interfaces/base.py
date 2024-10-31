"""Base interfaces and abstract classes"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict

T = TypeVar('T')

class BaseInterface(ABC):
    """Base interface with common methods"""
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the component"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate component configuration"""
        pass 