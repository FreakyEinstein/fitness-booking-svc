from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..utils.jwt import get_current_user
from ..models.income import IncomeSource, IncomeSourceUpdate
from ..services.income_service import (
    create_income_source,
    get_income_sources_by_user,
    get_income_source_by_id,
    update_income_source,
    delete_income_source
)

router = APIRouter()


@router.post("")
async def add_income_source(
    income_source: IncomeSource,
    token=Depends(get_current_user)
):
    """
    Add a new income source for the authenticated user.
    
    - **name**: Name of the income source
    - **amount**: Income amount (must be positive)
    - **frequency**: How often this income occurs (one_time, weekly, monthly, yearly)
    - **description**: Optional description
    """
    return create_income_source(token["email"], income_source)


@router.get("")
async def get_my_income_sources(
    token=Depends(get_current_user)
) -> List[dict]:
    """
    Get all income sources for the authenticated user.
    """
    return get_income_sources_by_user(token["email"])


@router.get("/{income_source_id}")
async def get_income_source(
    income_source_id: str,
    token=Depends(get_current_user)
):
    """
    Get a specific income source by ID.
    """
    income_source = get_income_source_by_id(token["email"], income_source_id)
    if not income_source:
        raise HTTPException(status_code=404, detail="Income source not found")
    return income_source


@router.put("/{income_source_id}")
async def update_my_income_source(
    income_source_id: str,
    update_data: IncomeSourceUpdate,
    token=Depends(get_current_user)
):
    """
    Update an existing income source.
    
    Only provide the fields you want to update.
    """
    return update_income_source(token["email"], income_source_id, update_data)


@router.delete("/{income_source_id}")
async def delete_my_income_source(
    income_source_id: str,
    token=Depends(get_current_user)
):
    """
    Delete an income source.
    """
    return delete_income_source(token["email"], income_source_id)