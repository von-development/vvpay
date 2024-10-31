import pytest
from pathlib import Path
from datetime import datetime
import json
from decimal import Decimal

from utils.inspect_schema import inspect_table_schema
from models.models import (
    MetaTable,
    PDFExtraction,
    ValidationResult,
    PaymentRecord,
    ProcessingLog,
    PaymentType
)

@pytest.fixture
def db_schema():
    """Get database schema information"""
    return inspect_table_schema("pdf_extractions")

@pytest.fixture
def sample_extraction_data():
    """Create sample extraction data"""
    return {
        "file_name": "test.pdf",
        "cnpj": "12345678901234",
        "valor": Decimal("1000.00"),
        "competence": "01/08/2024",
        "payee_name": "Test Company",
        "raw_text": "Sample PDF content",
        "confidence_score": Decimal("95.0"),
        "status": "pending"
    }

@pytest.fixture
def sample_meta_record():
    """Create a sample meta table record"""
    return MetaTable(
        id="test-123",
        nome="Test Company",
        tipo=PaymentType.PC,
        cpf_cnpj="12345678901234",
        pix="test@pix.com",
        ago_pc=1000.0,
        created_at=datetime.utcnow()
    )

@pytest.fixture
def sample_pdf_extraction():
    """Create a sample PDF extraction"""
    return PDFExtraction(
        id="test-456",
        file_name="test.pdf",
        cnpj="12345678901234",
        valor=1000.0,
        competence="01/08/2024",
        payee_name="Test Company",
        raw_text="Sample PDF content",
        confidence_score=95.0,
        created_at=datetime.utcnow()
    )

@pytest.fixture
def sample_validation_result(sample_pdf_extraction):
    """Create a sample validation result"""
    return ValidationResult(
        id="test-789",
        pdf_extraction_id=sample_pdf_extraction.id,
        is_valid=True,
        validation_errors=[],
        validated_at=datetime.utcnow()
    ) 