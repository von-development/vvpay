"""Meta table model"""
from typing import Optional
from decimal import Decimal
from pydantic import Field

from .base import DBModelBase

class MetaTable(DBModelBase):
    """Provider metadata and payment information"""
    nome: str = Field(..., description="Provider name")
    cpf_cnpj: str = Field(..., description="CPF or CNPJ", index=True)
    tipo: str = Field(..., description="Provider type")
    pix: str = Field(..., description="PIX key")
    ago_pc: Optional[Decimal] = Field(default=None, description="August PC amount")
    ago_bn: Optional[Decimal] = Field(default=None, description="August Bonus amount")
    ago_re: Optional[Decimal] = Field(default=None, description="August Reembolso amount")
    out_pc: Optional[Decimal] = Field(default=None, description="Outubro PC amount")

    class Config:
        """Model configuration"""
        json_schema_extra = {
            "example": {
                "nome": "Provider Name",
                "cpf_cnpj": "12345678901234",
                "tipo": "PJ",
                "pix": "pix@example.com",
                "ago_pc": 1000.00,
                "ago_bn": None,
                "ago_re": None,
                "out_pc": None
            }
        } 