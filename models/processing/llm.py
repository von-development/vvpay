"""LLM-specific models"""
from typing import Optional, Dict, TypedDict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

class ExtractionState(TypedDict):
    """State for LLM extraction process"""
    file_name: str
    raw_text: str
    llm_response: Optional[str]
    structured_data: Optional[Dict]
    error: Optional[str]

class LLMInput(BaseModel):
    """Input structure for LLM processing"""
    text: str = Field(..., description="Text to process")
    context: Optional[str] = Field(default=None, description="Additional context")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens for response")
    temperature: float = Field(default=0.0, description="LLM temperature")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")

    model_config = ConfigDict(protected_namespaces=())

class LLMOutput(BaseModel):
    """Output structure from LLM"""
    content: str = Field(..., description="LLM response content")
    llm_name: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(default=None, description="Number of tokens used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(protected_namespaces=())

class InvoiceData(BaseModel):
    """Structure for invoice data extracted by LLM"""
    cnpj: str = Field(..., description="14-digit CNPJ number")
    valor: float = Field(..., description="Payment amount")
    competence: str = Field(..., description="MM/YYYY format")
    payee_name: str = Field(..., description="Provider name")
    description: str = Field(..., description="Service description")
    payment_type: str = Field(..., description="pc/reembolso/bonus")
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence score of extraction"
    )

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Validate CNPJ format"""
        cnpj = re.sub(r'[^0-9]', '', v)
        if len(cnpj) != 14:
            raise ValueError("CNPJ must have exactly 14 digits")
        return cnpj

    @field_validator('competence')
    @classmethod
    def validate_competence(cls, v: str) -> str:
        """Validate competence format"""
        if not re.match(r'^\d{2}/\d{4}$', v):
            raise ValueError("Competence must be in MM/YYYY format")
        return v

    @field_validator('payment_type')
    @classmethod
    def validate_payment_type(cls, v: str) -> str:
        """Validate payment type"""
        valid_types = {'pc', 'reembolso', 'bonus'}
        if v.lower() not in valid_types:
            raise ValueError(f"Payment type must be one of: {', '.join(valid_types)}")
        return v.lower()

def create_initial_state(file_name: str, raw_text: str) -> ExtractionState:
    """Create initial state for LLM processing"""
    return {
        "file_name": file_name,
        "raw_text": raw_text,
        "llm_response": None,
        "structured_data": None,
        "error": None
    }