import pytz
import json
from pathlib import Path
from ..models.classes import Class
from ..utils.timezone_utils import (
    parse_ist_iso_to_utc_iso,
    parse_utc_iso_to_local_str,
)
from ..config import Settings

settings = Settings()
APP_TIMEZONE = pytz.timezone(settings.app_timezone)

CLASSES_FILE = Path("app/storage/classes.json")


def parse_datetime_string_to_utc_iso(value):
    """
    Accepts IST ISO string (e.g. "2025-07-28T05:30:00") and returns UTC ISO string.
    """
    try:
        dt_utc_iso = parse_ist_iso_to_utc_iso(value)
        # Check if datetime is in the future
        from datetime import datetime, timezone as dt_timezone
        if datetime.fromisoformat(dt_utc_iso).astimezone(dt_timezone.utc) < datetime.now(dt_timezone.utc):
            raise ValueError("Cannot create a class in the past")
        return dt_utc_iso
    except Exception as e:
        raise ValueError(f"Invalid datetime format: {e}")


def decrement_remaining_slots(class_id: str):
    # Load existing classes
    with open(CLASSES_FILE, "r") as f:
        classes = json.load(f)

    updated = False

    for cls in classes:
        if cls["id"] == class_id:
            if cls["remaining_slots"] > 0:
                cls["remaining_slots"] -= 1
                updated = True
            break

    if updated:
        with open(CLASSES_FILE, "w") as f:
            json.dump(classes, f, indent=4)
        print(f"Class {class_id} updated: remaining_slots decremented.")
    else:
        print(
            f"Class {class_id} not updated. Either not found or already full.")


def load_classes():
    """
    Load all classes from storage (no timezone conversion).
    """
    if CLASSES_FILE.exists():
        with open(CLASSES_FILE, "r") as f:
            return json.load(f)
    return []


def save_classes(classes):
    """
    Save the list of classes to storage, sorted by UTC datetime.
    """
    classes = sorted(classes, key=lambda x: x["datetime_of_class"])
    with open(CLASSES_FILE, "w") as f:
        json.dump(classes, f, indent=4)


def get_class_by_id(class_id: str, timezone):
    """
    Get a class by its ID, with datetime localized for display.
    """
    classes = load_classes()
    cl = next((cl for cl in classes if cl["id"] == class_id), None)
    if cl and timezone:
        cl = {
            **cl, "datetime_of_class": parse_utc_iso_to_local_str(cl["datetime_of_class"], timezone)}
    return cl


def create_new_class(session_class: Class, token: dict):
    """
    Create a new class. Input datetime must be IST ISO string.
    """
    doc = {k: v for k, v in session_class.__dict__.items() if v is not None}
    doc['remaining_slots'] = doc["total_slots"]
    doc['instructor'] = token['name']
    doc['instructor_email'] = token['email']
    # Convert input IST ISO string to UTC ISO string for storage
    doc["datetime_of_class"] = parse_datetime_string_to_utc_iso(
        doc["datetime_of_class"])
    classes = load_classes()
    classes.append(doc)
    save_classes(classes)
    return {'success': True, 'detail': "Class successfully added"}


def get_classes(timezone: str = None):
    """
    Get all classes, with datetimes localized for display.
    """
    classes = load_classes()
    if timezone:
        for cl in classes:
            cl["datetime_of_class"] = parse_utc_iso_to_local_str(
                cl["datetime_of_class"], timezone)
    return classes
