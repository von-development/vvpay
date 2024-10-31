"""Meta table model for provider information"""
from typing import Optional
from decimal import Decimal
from pydantic import Field

from .base import DBModelBase
from ..service.enums import PaymentType

class MetaTable(DBModelBase):
    """
    Provider metadata and payment information.
    Maps to 'meta_table' in database.
    """
    nome: str = Field(..., description="Provider name")
    cpf_cnpj: str = Field(..., description="CPF or CNPJ", index=True)
    tipo: PaymentType = Field(..., description="Payment type")
    pix: str = Field(..., description="PIX key")
    ago_pc: Optional[Decimal] = Field(default=None, description="PC amount")
    ago_bn: Optional[Decimal] = Field(default=None, description="Bonus amount")
    ago_re: Optional[Decimal] = Field(default=None, description="Reembolso amount") 