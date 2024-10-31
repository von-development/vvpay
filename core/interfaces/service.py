"""Service layer interfaces"""
from typing import Optional, Dict, Generic, TypeVar
from abc import abstractmethod, ABC

from .base import BaseInterface
from models.db.extraction import PDFExtraction
from models.db.validation import ValidationResult

T = TypeVar('T')

class ExtractorInterface(BaseInterface):
    """Interface for extraction services"""
    @abstractmethod
    def extract_data(
        self,
        text: str,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> PDFExtraction:
        """Extract data from text"""
        pass

class ProcessorInterface(Generic[T], ABC):
    """Interface for document processors"""
    @abstractmethod
    def initialize(self) -> None:
        """Initialize processor components"""
        pass

    @abstractmethod
    def validate_config(self) -> None:
        """Validate processor configuration"""
        pass

    @abstractmethod
    def process_document(
        self,
        content: bytes,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> T:
        """Process a document and extract information"""
        pass

class ValidationInterface(BaseInterface):
    """Interface for validation services"""
    @abstractmethod
    def validate(
        self,
        extraction: PDFExtraction,
        metadata: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate extracted data"""
        pass 