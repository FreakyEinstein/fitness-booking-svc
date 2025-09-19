import json
import uuid
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Optional

from fastapi import HTTPException

from ..models.budget import BudgetCategory, BudgetCategoryUpdate

BUDGET_CATEGORIES_FILE = Path("app/storage/budget_categories.json")


def load_budget_categories():
    """Load all budget categories from storage."""
    if BUDGET_CATEGORIES_FILE.exists():
        with open(BUDGET_CATEGORIES_FILE, "r") as f:
            return json.load(f)
    return []


def save_budget_categories(budget_categories):
    """Save budget categories to storage."""
    with open(BUDGET_CATEGORIES_FILE, "w") as f:
        json.dump(budget_categories, f, indent=4)


def create_budget_category(user_email: str, budget_category: BudgetCategory):
    """Create a new budget category for a user."""
    budget_categories = load_budget_categories()
    
    # Check if budget category with same name exists for this user
    existing = next((item for item in budget_categories 
                    if item["user_email"] == user_email and item["name"] == budget_category.name), None)
    if existing:
        raise HTTPException(status_code=409, detail="Budget category with this name already exists")
    
    new_budget_category = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "name": budget_category.name,
        "allocated_amount": budget_category.allocated_amount,
        "limit": budget_category.limit,
        "description": budget_category.description,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    budget_categories.append(new_budget_category)
    save_budget_categories(budget_categories)
    
    return {"success": True, "message": "Budget category created successfully", "id": new_budget_category["id"]}


def get_budget_categories_by_user(user_email: str) -> List[dict]:
    """Get all budget categories for a user."""
    budget_categories = load_budget_categories()
    user_budget_categories = [item for item in budget_categories if item["user_email"] == user_email]
    return user_budget_categories


def get_budget_category_by_id(user_email: str, budget_category_id: str) -> Optional[dict]:
    """Get a specific budget category by ID for a user."""
    budget_categories = load_budget_categories()
    return next((item for item in budget_categories 
                if item["user_email"] == user_email and item["id"] == budget_category_id), None)


def get_budget_category_by_name(user_email: str, category_name: str) -> Optional[dict]:
    """Get a specific budget category by name for a user."""
    budget_categories = load_budget_categories()
    return next((item for item in budget_categories 
                if item["user_email"] == user_email and item["name"] == category_name), None)


def update_budget_category(user_email: str, budget_category_id: str, update_data: BudgetCategoryUpdate):
    """Update a budget category."""
    budget_categories = load_budget_categories()
    
    for item in budget_categories:
        if item["user_email"] == user_email and item["id"] == budget_category_id:
            # Check for name conflicts if name is being updated
            if update_data.name and update_data.name != item["name"]:
                existing = next((category for category in budget_categories 
                               if category["user_email"] == user_email and category["name"] == update_data.name), None)
                if existing:
                    raise HTTPException(status_code=409, detail="Budget category with this name already exists")
            
            # Update only provided fields
            if update_data.name is not None:
                item["name"] = update_data.name
            if update_data.allocated_amount is not None:
                item["allocated_amount"] = update_data.allocated_amount
            if update_data.limit is not None:
                item["limit"] = update_data.limit
            if update_data.description is not None:
                item["description"] = update_data.description
            
            item["updated_at"] = datetime.now(UTC).isoformat()
            save_budget_categories(budget_categories)
            return {"success": True, "message": "Budget category updated successfully"}
    
    raise HTTPException(status_code=404, detail="Budget category not found")


def delete_budget_category(user_email: str, budget_category_id: str):
    """Delete a budget category."""
    budget_categories = load_budget_categories()
    
    initial_length = len(budget_categories)
    budget_categories = [item for item in budget_categories 
                        if not (item["user_email"] == user_email and item["id"] == budget_category_id)]
    
    if len(budget_categories) == initial_length:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    save_budget_categories(budget_categories)
    return {"success": True, "message": "Budget category deleted successfully"}