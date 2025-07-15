from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FinancialProduct(BaseModel):
    """Abstract representation of any product a user
    holds at a financial institution."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    institution: Literal["itau", "nubank"]
    product_type: Literal[
        "checking_account",
        "savings_account",
        "credit_card",
        "loan",
        "investment",
    ]
    name: str = Field(..., description="Friendly label shown to the user")
    account_number: Optional[str] = Field(
        None, description="Masked identifier when permitted"
    )

    # monetary snapshot
    balance: Decimal = Field(
        ...,
        description="Current principal/outstanding balance")
    currency: str = Field("COP", min_length=3, max_length=3)
    credit_limit: Optional[Decimal] = Field(
        None, description="For revolving credit products"
    )
    interest_rate: Optional[Decimal] = Field(
        None, description="APR or APY expressed as decimal (0.125 = 12.5%)"
    )

    opened_date: Optional[date] = None
    due_date: Optional[date] = Field(
        None, description="Next payment or statement due date"
    )

    tags: list[str] = Field(
        default_factory=list,
        description="User-defined labels")
    metadata: dict = Field(default_factory=dict)

    model_config = {"json_schema_extra": {"examples": [
        {
            "institution": "itau",
            "product_type": "credit_card",
            "name": "Itaú Mastercard Black",
            "account_number": "****9876",
            "balance": "155000.25",
            "currency": "COP",
            "credit_limit": "2000000",
            "interest_rate": "0.0245",
            "due_date": "2025-07-27",
            "tags": ["travel"],
        }
    ]}}
