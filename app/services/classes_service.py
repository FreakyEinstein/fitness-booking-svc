import pytz
from datetime import datetime
import json
from pathlib import Path
from ..models.classes import Class
from ..utils.classes import convert_utc_to_local
from ..config import Settings

settings = Settings()
APP_TIMEZONE = pytz.timezone(settings.app_timezone)

CLASSES_FILE = Path("app/storage/classes.json")


def parse_datetime_string_to_iso(value):
    """
    Convert from IST string format 'DD-MM-YYYY HH:mm' to UTC ISO format string.
    """
    try:
        # Parse the naive datetime
        dt_naive = datetime.strptime(value, "%d-%m-%Y %H:%M")
        # Localize to IST
        dt_ist = APP_TIMEZONE.localize(dt_naive)
        # Convert to UTC
        dt_utc = dt_ist.astimezone(pytz.UTC)

        # Check if datetime is in the future
        if dt_utc < datetime.now(pytz.UTC):
            raise ValueError("Cannot create a class in the past")

        return dt_utc.isoformat()
    except Exception as e:
        raise ValueError(f"Invalid datetime format: {e}")


def load_classes(timezone: str = None):
    if CLASSES_FILE.exists():
        with open(CLASSES_FILE, "r") as f:
            return [
                {**doc,
                 "datetime_of_class": convert_utc_to_local(doc["datetime_of_class"], timezone)}
                for doc in json.load(f)
            ]
    return []


def save_classes(classes):
    classes = sorted(classes, key=lambda x: x["datetime_of_class"])
    with open(CLASSES_FILE, "w") as f:
        json.dump(classes, f, indent=4)


def get_class_by_id():
    return


def create_new_class(session_class: Class):
    doc = {k: v for k, v in session_class.__dict__.items() if v is not None}
    doc['remaining_slots'] = 0
    classes = [{**record, "datetime_of_class": parse_datetime_string_to_iso(
        record["datetime_of_class"])} for record in load_classes()]
    classes.append(doc)
    save_classes(classes)
    return {'success': True, 'detail': "Class successfully added"}


def get_classes(timezone: str = None):
    classes = load_classes(timezone)
    return classes
