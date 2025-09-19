import json
import uuid
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Optional

from fastapi import HTTPException

from ..models.transaction import Transaction, TransactionUpdate
from .budget_service import get_budget_category_by_name
from .income_service import get_income_sources_by_user

TRANSACTIONS_FILE = Path("app/storage/transactions.json")


def load_transactions():
    """Load all transactions from storage."""
    if TRANSACTIONS_FILE.exists():
        with open(TRANSACTIONS_FILE, "r") as f:
            return json.load(f)
    return []


def save_transactions(transactions):
    """Save transactions to storage."""
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(transactions, f, indent=4)


def get_total_spent_in_category(user_email: str, category_name: str) -> float:
    """Calculate total spent in a specific budget category."""
    transactions = load_transactions()
    total = 0.0
    
    for transaction in transactions:
        if (transaction["user_email"] == user_email and 
            transaction["transaction_type"] == "expense" and 
            transaction["category"] == category_name):
            total += transaction["amount"]
    
    return total


def check_budget_limit(user_email: str, category_name: str, new_amount: float) -> dict:
    """Check if a transaction would exceed the budget limit."""
    budget_category = get_budget_category_by_name(user_email, category_name)
    
    if not budget_category:
        return {"within_limit": True, "message": "No budget category found"}
    
    if not budget_category.get("limit"):
        return {"within_limit": True, "message": "No limit set for this category"}
    
    current_spent = get_total_spent_in_category(user_email, category_name)
    total_after_transaction = current_spent + new_amount
    limit = budget_category["limit"]
    
    if total_after_transaction > limit:
        return {
            "within_limit": False,
            "message": f"Transaction would exceed budget limit. Current spent: ${current_spent:.2f}, "
                      f"Transaction: ${new_amount:.2f}, Total: ${total_after_transaction:.2f}, "
                      f"Limit: ${limit:.2f}, Overage: ${total_after_transaction - limit:.2f}"
        }
    
    return {"within_limit": True, "message": "Transaction is within budget limit"}


def create_transaction(user_email: str, transaction: Transaction):
    """Create a new transaction for a user."""
    transactions = load_transactions()
    
    # Validate category exists
    if transaction.transaction_type == "expense":
        # Check if budget category exists
        budget_category = get_budget_category_by_name(user_email, transaction.category)
        if not budget_category:
            raise HTTPException(status_code=404, detail=f"Budget category '{transaction.category}' not found")
        
        # Check budget limit
        limit_check = check_budget_limit(user_email, transaction.category, transaction.amount)
        
    elif transaction.transaction_type == "income":
        # Check if income source exists
        income_sources = get_income_sources_by_user(user_email)
        if not any(source["name"] == transaction.category for source in income_sources):
            raise HTTPException(status_code=404, detail=f"Income source '{transaction.category}' not found")
        limit_check = {"within_limit": True, "message": "Income transaction"}
    
    # Use provided date or current datetime
    transaction_date = transaction.date if transaction.date else datetime.now(UTC)
    
    new_transaction = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "category": transaction.category,
        "description": transaction.description,
        "date": transaction_date.isoformat() if hasattr(transaction_date, 'isoformat') else transaction_date,
        "created_at": datetime.now(UTC).isoformat(),
        "budget_limit_exceeded": not limit_check["within_limit"],
        "limit_check_message": limit_check["message"]
    }
    
    transactions.append(new_transaction)
    save_transactions(transactions)
    
    response = {
        "success": True, 
        "message": "Transaction logged successfully", 
        "id": new_transaction["id"],
        "budget_status": limit_check
    }
    
    if not limit_check["within_limit"]:
        response["warning"] = "Budget limit exceeded for this category"
    
    return response


def get_transactions_by_user(user_email: str) -> List[dict]:
    """Get all transactions for a user, sorted by date (newest first)."""
    transactions = load_transactions()
    user_transactions = [item for item in transactions if item["user_email"] == user_email]
    
    # Sort by date, newest first
    user_transactions.sort(key=lambda x: x["date"], reverse=True)
    return user_transactions


def get_transaction_by_id(user_email: str, transaction_id: str) -> Optional[dict]:
    """Get a specific transaction by ID for a user."""
    transactions = load_transactions()
    return next((item for item in transactions 
                if item["user_email"] == user_email and item["id"] == transaction_id), None)


def update_transaction(user_email: str, transaction_id: str, update_data: TransactionUpdate):
    """Update a transaction."""
    transactions = load_transactions()
    
    for item in transactions:
        if item["user_email"] == user_email and item["id"] == transaction_id:
            # Validate category if it's being updated
            if update_data.category and update_data.transaction_type:
                transaction_type = update_data.transaction_type
            else:
                transaction_type = item["transaction_type"]
            
            if update_data.category:
                category = update_data.category
                if transaction_type == "expense":
                    budget_category = get_budget_category_by_name(user_email, category)
                    if not budget_category:
                        raise HTTPException(status_code=404, detail=f"Budget category '{category}' not found")
                elif transaction_type == "income":
                    income_sources = get_income_sources_by_user(user_email)
                    if not any(source["name"] == category for source in income_sources):
                        raise HTTPException(status_code=404, detail=f"Income source '{category}' not found")
            
            # Update only provided fields
            if update_data.amount is not None:
                item["amount"] = update_data.amount
            if update_data.transaction_type is not None:
                item["transaction_type"] = update_data.transaction_type
            if update_data.category is not None:
                item["category"] = update_data.category
            if update_data.description is not None:
                item["description"] = update_data.description
            if update_data.date is not None:
                item["date"] = update_data.date.isoformat() if hasattr(update_data.date, 'isoformat') else update_data.date
            
            item["updated_at"] = datetime.now(UTC).isoformat()
            
            # Recalculate budget limit check if it's an expense
            if item["transaction_type"] == "expense":
                # Get current total excluding this transaction
                current_spent = get_total_spent_in_category(user_email, item["category"])
                current_spent -= item["amount"]  # Subtract the old amount
                limit_check = check_budget_limit(user_email, item["category"], item["amount"])
                item["budget_limit_exceeded"] = not limit_check["within_limit"]
                item["limit_check_message"] = limit_check["message"]
            
            save_transactions(transactions)
            return {"success": True, "message": "Transaction updated successfully"}
    
    raise HTTPException(status_code=404, detail="Transaction not found")


def delete_transaction(user_email: str, transaction_id: str):
    """Delete a transaction."""
    transactions = load_transactions()
    
    initial_length = len(transactions)
    transactions = [item for item in transactions 
                   if not (item["user_email"] == user_email and item["id"] == transaction_id)]
    
    if len(transactions) == initial_length:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    save_transactions(transactions)
    return {"success": True, "message": "Transaction deleted successfully"}


def get_budget_summary(user_email: str) -> dict:
    """Get a summary of budget usage for all categories."""
    transactions = load_transactions()
    from .budget_service import get_budget_categories_by_user
    
    budget_categories = get_budget_categories_by_user(user_email)
    summary = []
    
    for category in budget_categories:
        total_spent = get_total_spent_in_category(user_email, category["name"])
        limit = category.get("limit")
        allocated = category.get("allocated_amount", 0)
        
        category_summary = {
            "category_name": category["name"],
            "allocated_amount": allocated,
            "limit": limit,
            "total_spent": total_spent,
            "remaining_allocated": allocated - total_spent,
            "within_limit": True if not limit else total_spent <= limit,
            "limit_exceeded_by": max(0, total_spent - limit) if limit else 0
        }
        
        summary.append(category_summary)
    
    return {"budget_summary": summary}