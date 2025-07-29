from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class Transaction(BaseModel):
    """A single ledger entry coming from Itaú, Nu Bank,
    or any future institution."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Internal primary key")
    institution: Literal["itau", "nubank"] = Field(
        ...,
        description="Data source tag")
    account_id: str = Field(
        ...,
        description="Bank-side account or card identifier")

    # timestamps
    txn_date: date = Field(
        ...,
        description="Bank-posted date (local to institution)")
    posted_at: datetime = Field(default_factory=datetime.utcnow,
                                description="Ingestion timestamp (UTC)")

    # money & classification
    amount: Decimal = Field(
        ...,
        description="Signed amount; debits are negative")
    currency: str = Field("COP", min_length=3, max_length=3)
    txn_type: Literal["debit", "credit"] = Field(..., )
    category: Optional[str] = Field(
        None, description="Normalized category label")
    balance_after: Optional[Decimal] = Field(
        None, description="Running balance after this txn, if provided by bank"
    )

    # descriptive info
    description: str = Field(..., description="Raw merchant or memo line")
    metadata: dict = Field(
        default_factory=dict,
        description="Free-form key/value pairs—e.g. merchant_id, geo, tags",
    )

    @model_validator(mode="after")
    def ensure_sign_matches_type(self) -> "Transaction":
        if (self.txn_type == "debit" and self.amount > 0) or (
            self.txn_type == "credit" and self.amount < 0
        ):
            raise ValueError("amount sign does not match txn_type")
        return self

    model_config = {"json_schema_extra": {"examples": [
        {
            "institution": "nubank",
            "account_id": "****1234",
            "txn_date": "2025-07-13",
            "amount": "-42000.00",
            "currency": "COP",
            "type": "debit",
            "description": "Uber Eats - Bogotá",
            "category": "food_delivery",
        }
    ]}}
