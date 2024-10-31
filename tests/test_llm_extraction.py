"""Tests for LLM extraction functionality"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
from datetime import datetime

from services.llm_extraction import LLMExtractor, parse_json_response
from models.models import LLMOutput, Status, PDFExtraction
from core.exceptions import ExtractionError

# Sample invoice text for testing
SAMPLE_INVOICE_TEXT = """
PREFEITURA DO RECIFE
SECRETARIA DE FINANÇAS
NOTA FISCAL DE SERVIÇOS ELETRÔNICA - NFS-e

PRESTADOR DE SERVIÇOS
Nome/Razão Social: João Victor Coutinho Suassuna
CNPJ: 12345678901234
Endereço: Rua Teste, 123 - Recife/PE

TOMADOR DE SERVIÇOS
Nome/Razão Social: Exponencial TI Soluções Digitais LTDA
CNPJ: 26.846.328/0001-17

DISCRIMINAÇÃO DOS SERVIÇOS
Prestação de serviços de desenvolvimento de software
Valor do Serviço: R$ 5000,00
Competência: 08/2024
"""

@pytest.fixture
def llm_extractor():
    """Create LLMExtractor instance"""
    return LLMExtractor()

def test_parse_json_response():
    """Test JSON response parsing"""
    # Test valid JSON
    valid_json = '{"cnpj": "12345678901234", "valor": 5000.0}'
    result = parse_json_response(valid_json)
    assert result["cnpj"] == "12345678901234"
    assert result["valor"] == 5000.0

    # Test JSON with markdown
    markdown_json = '```json\n{"cnpj": "12345678901234", "valor": 5000.0}\n```'
    result = parse_json_response(markdown_json)
    assert result["cnpj"] == "12345678901234"
    assert result["valor"] == 5000.0

    # Test invalid JSON
    with pytest.raises(ExtractionError):
        parse_json_response("invalid json")

def test_llm_extraction(llm_extractor):
    """Test LLM extraction functionality"""
    try:
        # Verify model name
        assert llm_extractor.llm.model_name == "gpt-4o-mini"
        
        # Test extraction
        result = llm_extractor.extract_data(
            text=SAMPLE_INVOICE_TEXT,
            filename="test_invoice.pdf"
        )
        
        # Verify result type
        assert isinstance(result, PDFExtraction)
        
        # Verify extracted fields
        assert result.cnpj == "12345678901234"
        assert result.valor == 5000.0
        assert result.competence == "08/2024"
        assert result.payee_name == "João Victor Coutinho Suassuna"
        assert result.status == Status.EXTRACTED
        assert result.payment_type == "pc"  # Default for regular payment
        
        # Verify timestamps
        assert result.extracted_at is not None
        
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

def test_payment_type_detection(llm_extractor):
    """Test payment type detection"""
    # Test bonus detection
    bonus_text = SAMPLE_INVOICE_TEXT.replace(
        "Prestação de serviços",
        "Pagamento de bônus por desempenho"
    )
    result = llm_extractor.extract_data(
        text=bonus_text,
        filename="bonus_payment.pdf"
    )
    assert result.payment_type == "bonus"
    
    # Test reembolso detection
    reembolso_text = SAMPLE_INVOICE_TEXT.replace(
        "Prestação de serviços",
        "Reembolso de despesas"
    )
    result = llm_extractor.extract_data(
        text=reembolso_text,
        filename="reembolso_payment.pdf"
    )
    assert result.payment_type == "reembolso"

def test_error_handling(llm_extractor):
    """Test error handling"""
    # Test empty text
    with pytest.raises(ExtractionError) as exc_info:
        llm_extractor.extract_data(
            text="",
            filename="empty.pdf"
        )
    assert "Empty text content" in str(exc_info.value)
    
    # Test invalid text
    with pytest.raises(ExtractionError):
        llm_extractor.extract_data(
            text="Invalid content",
            filename="invalid.pdf"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 