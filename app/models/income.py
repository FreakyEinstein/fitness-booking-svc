from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class IncomeFrequency(str, Enum):
    ONE_TIME = "one_time"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class IncomeSource(BaseModel):
    """
    Income source for a user.
    
    - `name`: Name of the income source
    - `amount`: Amount of income
    - `frequency`: How often this income occurs
    - `description`: Optional description
    """
    name: str = Field(..., description="Name of the income source")
    amount: float = Field(..., gt=0, description="Income amount (must be positive)")
    frequency: IncomeFrequency = Field(..., description="Income frequency")
    description: Optional[str] = Field(None, description="Optional description")


class IncomeSourceUpdate(BaseModel):
    """
    Update model for income source.
    """
    name: Optional[str] = Field(None, description="Name of the income source")
    amount: Optional[float] = Field(None, gt=0, description="Income amount (must be positive)")
    frequency: Optional[IncomeFrequency] = Field(None, description="Income frequency")
    description: Optional[str] = Field(None, description="Optional description")