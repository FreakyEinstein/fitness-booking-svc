from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(BaseModel):
    """
    Transaction record for a user.
    
    - `amount`: Transaction amount
    - `transaction_type`: Whether it's income or expense
    - `category`: Budget category (for expenses) or income source (for income)
    - `description`: Optional description
    - `date`: Optional transaction date (defaults to now)
    """
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    category: str = Field(..., description="Budget category for expenses or income source for income")
    description: Optional[str] = Field(None, description="Optional description")
    date: Optional[datetime] = Field(None, description="Transaction date (defaults to current time)")


class TransactionUpdate(BaseModel):
    """
    Update model for transaction.
    """
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount (must be positive)")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type")
    category: Optional[str] = Field(None, description="Budget category for expenses or income source for income")
    description: Optional[str] = Field(None, description="Optional description")
    date: Optional[datetime] = Field(None, description="Transaction date")