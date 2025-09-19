from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..utils.jwt import get_current_user
from ..models.budget import BudgetCategory, BudgetCategoryUpdate
from ..services.budget_service import (
    create_budget_category,
    get_budget_categories_by_user,
    get_budget_category_by_id,
    update_budget_category,
    delete_budget_category
)

router = APIRouter()


@router.post("")
async def add_budget_category(
    budget_category: BudgetCategory,
    token=Depends(get_current_user)
):
    """
    Add a new budget category for the authenticated user.
    
    - **name**: Name of the budget category
    - **allocated_amount**: Amount allocated for this category
    - **limit**: Optional spending limit for this category
    - **description**: Optional description
    """
    return create_budget_category(token["email"], budget_category)


@router.get("")
async def get_my_budget_categories(
    token=Depends(get_current_user)
) -> List[dict]:
    """
    Get all budget categories for the authenticated user.
    """
    return get_budget_categories_by_user(token["email"])


@router.get("/{budget_category_id}")
async def get_budget_category(
    budget_category_id: str,
    token=Depends(get_current_user)
):
    """
    Get a specific budget category by ID.
    """
    budget_category = get_budget_category_by_id(token["email"], budget_category_id)
    if not budget_category:
        raise HTTPException(status_code=404, detail="Budget category not found")
    return budget_category


@router.put("/{budget_category_id}")
async def update_my_budget_category(
    budget_category_id: str,
    update_data: BudgetCategoryUpdate,
    token=Depends(get_current_user)
):
    """
    Update an existing budget category.
    
    Only provide the fields you want to update.
    """
    return update_budget_category(token["email"], budget_category_id, update_data)


@router.delete("/{budget_category_id}")
async def delete_my_budget_category(
    budget_category_id: str,
    token=Depends(get_current_user)
):
    """
    Delete a budget category.
    """
    return delete_budget_category(token["email"], budget_category_id)