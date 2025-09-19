import json
import uuid
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Optional

from fastapi import HTTPException

from ..models.income import IncomeSource, IncomeSourceUpdate

INCOME_SOURCES_FILE = Path("app/storage/income_sources.json")


def load_income_sources():
    """Load all income sources from storage."""
    if INCOME_SOURCES_FILE.exists():
        with open(INCOME_SOURCES_FILE, "r") as f:
            return json.load(f)
    return []


def save_income_sources(income_sources):
    """Save income sources to storage."""
    with open(INCOME_SOURCES_FILE, "w") as f:
        json.dump(income_sources, f, indent=4)


def create_income_source(user_email: str, income_source: IncomeSource):
    """Create a new income source for a user."""
    income_sources = load_income_sources()
    
    # Check if income source with same name exists for this user
    existing = next((item for item in income_sources 
                    if item["user_email"] == user_email and item["name"] == income_source.name), None)
    if existing:
        raise HTTPException(status_code=409, detail="Income source with this name already exists")
    
    new_income_source = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "name": income_source.name,
        "amount": income_source.amount,
        "frequency": income_source.frequency,
        "description": income_source.description,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    income_sources.append(new_income_source)
    save_income_sources(income_sources)
    
    return {"success": True, "message": "Income source created successfully", "id": new_income_source["id"]}


def get_income_sources_by_user(user_email: str) -> List[dict]:
    """Get all income sources for a user."""
    income_sources = load_income_sources()
    user_income_sources = [item for item in income_sources if item["user_email"] == user_email]
    return user_income_sources


def get_income_source_by_id(user_email: str, income_source_id: str) -> Optional[dict]:
    """Get a specific income source by ID for a user."""
    income_sources = load_income_sources()
    return next((item for item in income_sources 
                if item["user_email"] == user_email and item["id"] == income_source_id), None)


def update_income_source(user_email: str, income_source_id: str, update_data: IncomeSourceUpdate):
    """Update an income source."""
    income_sources = load_income_sources()
    
    for item in income_sources:
        if item["user_email"] == user_email and item["id"] == income_source_id:
            # Check for name conflicts if name is being updated
            if update_data.name and update_data.name != item["name"]:
                existing = next((source for source in income_sources 
                               if source["user_email"] == user_email and source["name"] == update_data.name), None)
                if existing:
                    raise HTTPException(status_code=409, detail="Income source with this name already exists")
            
            # Update only provided fields
            if update_data.name is not None:
                item["name"] = update_data.name
            if update_data.amount is not None:
                item["amount"] = update_data.amount
            if update_data.frequency is not None:
                item["frequency"] = update_data.frequency
            if update_data.description is not None:
                item["description"] = update_data.description
            
            item["updated_at"] = datetime.now(UTC).isoformat()
            save_income_sources(income_sources)
            return {"success": True, "message": "Income source updated successfully"}
    
    raise HTTPException(status_code=404, detail="Income source not found")


def delete_income_source(user_email: str, income_source_id: str):
    """Delete an income source."""
    income_sources = load_income_sources()
    
    initial_length = len(income_sources)
    income_sources = [item for item in income_sources 
                     if not (item["user_email"] == user_email and item["id"] == income_source_id)]
    
    if len(income_sources) == initial_length:
        raise HTTPException(status_code=404, detail="Income source not found")
    
    save_income_sources(income_sources)
    return {"success": True, "message": "Income source deleted successfully"}