from pydantic import BaseModel, Field
from typing import Optional


class BudgetCategory(BaseModel):
    """
    Budget category for a user.
    
    - `name`: Name of the budget category
    - `allocated_amount`: Amount allocated for this category
    - `limit`: Optional spending limit for this category
    - `description`: Optional description
    """
    name: str = Field(..., description="Name of the budget category")
    allocated_amount: float = Field(..., ge=0, description="Amount allocated for this category")
    limit: Optional[float] = Field(None, ge=0, description="Optional spending limit")
    description: Optional[str] = Field(None, description="Optional description")


class BudgetCategoryUpdate(BaseModel):
    """
    Update model for budget category.
    """
    name: Optional[str] = Field(None, description="Name of the budget category")
    allocated_amount: Optional[float] = Field(None, ge=0, description="Amount allocated for this category")
    limit: Optional[float] = Field(None, ge=0, description="Optional spending limit")
    description: Optional[str] = Field(None, description="Optional description")