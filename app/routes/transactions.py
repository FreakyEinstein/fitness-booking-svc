from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..utils.jwt import get_current_user
from ..models.transaction import Transaction, TransactionUpdate
from ..services.transaction_service import (
    create_transaction,
    get_transactions_by_user,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    get_budget_summary
)

router = APIRouter()


@router.post("")
async def log_transaction(
    transaction: Transaction,
    token=Depends(get_current_user)
):
    """
    Log a new transaction for the authenticated user.
    
    - **amount**: Transaction amount (must be positive)
    - **transaction_type**: 'income' or 'expense'
    - **category**: Budget category name (for expenses) or income source name (for income)
    - **description**: Optional description
    - **date**: Optional transaction date (defaults to current time)
    
    The system will automatically check budget limits for expense transactions and flag violations.
    """
    return create_transaction(token["email"], transaction)


@router.get("")
async def get_my_transactions(
    token=Depends(get_current_user)
) -> List[dict]:
    """
    Get all transactions for the authenticated user, sorted by date (newest first).
    """
    return get_transactions_by_user(token["email"])


@router.get("/summary")
async def get_my_budget_summary(
    token=Depends(get_current_user)
):
    """
    Get a summary of budget usage across all categories for the authenticated user.
    
    Shows allocated amounts, spending limits, total spent, and budget violations.
    """
    return get_budget_summary(token["email"])


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    token=Depends(get_current_user)
):
    """
    Get a specific transaction by ID.
    """
    transaction = get_transaction_by_id(token["email"], transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}")
async def update_my_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    token=Depends(get_current_user)
):
    """
    Update an existing transaction.
    
    Only provide the fields you want to update.
    Budget limits will be recalculated for expense transactions.
    """
    return update_transaction(token["email"], transaction_id, update_data)


@router.delete("/{transaction_id}")
async def delete_my_transaction(
    transaction_id: str,
    token=Depends(get_current_user)
):
    """
    Delete a transaction.
    """
    return delete_transaction(token["email"], transaction_id)