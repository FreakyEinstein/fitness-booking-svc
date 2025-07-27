import json
from pathlib import Path
from datetime import datetime, timedelta, UTC

from fastapi import HTTPException

from ..services.classes_service import get_class_by_id, decrement_remaining_slots
from ..utils.classes import to_local, get_timezone_from_ip
from ..utils.timezone_utils import (
    parse_utc_iso_to_local_str,
)
from ..models.booking import Booking

from ..config import Settings

settings = Settings()
APP_TIMEZONE = settings.app_timezone

BOOKINGS_FILE = Path("app/storage/bookings.json")


def load_bookings():
    if BOOKINGS_FILE.exists():
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []


def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=4)


def book_class(token: dict, booking: Booking, timezone: str | None = APP_TIMEZONE):
    """
    Book a class for the user. Checks for overlapping bookings.
    """
    now_utc = datetime.now(UTC)

    class_details = get_class_by_id(booking.class_id, None)
    if not class_details:
        raise HTTPException(404, detail="Class Not available")

    if class_details.get("remaining_slots", 1) == 0:
        raise HTTPException(403, detail="Slots Not available")

    # check if the booking is for a past class
    class_start = datetime.fromisoformat(class_details["datetime_of_class"])
    if class_start < now_utc:
        raise HTTPException(403, detail="Cannot book a class in the past")

    # check if the class was already booked by the same user
    existing_bookings = load_bookings()
    for booking_record in existing_bookings:
        if booking_record["class_id"] == class_details["id"] and booking_record["user_email"] == token["email"]:
            raise HTTPException(
                403, detail="Class already booked by this user")

    # --- Overlap check ---
    # Get all bookings for this user
    user_bookings = [b for b in load_bookings() if b["user_email"]
                     == token["email"]]
    # Get the class time and duration
    class_start = datetime.fromisoformat(class_details["datetime_of_class"])
    class_end = class_start + \
        timedelta(hours=class_details.get("duration_in_hours", 1))

    for b in user_bookings:
        booked_class = get_class_by_id(b["class_id"], None)
        if not booked_class:
            continue
        booked_start = datetime.fromisoformat(
            booked_class["datetime_of_class"])
        booked_end = booked_start + \
            timedelta(hours=booked_class.get("duration_in_hours", 1))
        # Check for overlap
        if (class_start < booked_end) and (booked_start < class_end):
            raise HTTPException(
                status_code=409,
                detail=f"Booking overlaps with another class: {booked_class['name']} at {parse_utc_iso_to_local_str(booked_class['datetime_of_class'], timezone)}"
            )

    # Create and store booking
    doc = {
        "class_id": class_details["id"],
        "booked_at": now_utc.isoformat(),
        "user_email": token["email"],
        "user_name": token["name"]
    }
    bookings = load_bookings()
    bookings.append(doc)
    save_bookings(bookings)

    decrement_remaining_slots(doc["class_id"])

    return {"success": True, "message": "Booking successful"}


def populate_class_data(record, timezone):
    """
    Populate booking record with class details and localize datetimes for display.
    """
    # Use centralized conversion
    record["booked_at"] = parse_utc_iso_to_local_str(
        record["booked_at"], timezone)
    class_details = get_class_by_id(record["class_id"], None)
    record["class_name"] = class_details["name"]
    record["instructor"] = class_details["instructor"]
    record["datetime_of_class"] = parse_utc_iso_to_local_str(
        class_details["datetime_of_class"], timezone)
    return record


def get_bookings_by_user_email(email: str, timezone):
    """
    Get all bookings for a user, with datetimes localized for display.
    """
    # user gets the booking details in the ascending order of their booking time
    return sorted([populate_class_data(record, timezone) for record in load_bookings() if record["user_email"] == email], key=(lambda x: x["booked_at"]))


def get_class_booked_users(token: dict, class_id: str):
    """
    Returns a list of users who have booked a specific class, identified by class_id.
    Each user is represented as a dictionary containing their email and name.
    The returned list is sorted by booking time in descending order (most recent bookings first).
    """

    class_details = get_class_by_id(class_id, None)
    if not class_details or class_details.get("instructor_email") != token["email"]:
        raise HTTPException(
            403, detail="Not authorized")

    bookings = load_bookings()
    users = [
        {
            "user_email": record["user_email"],
            "user_name": record.get("user_name", "")
        }
        for record in bookings if record["class_id"] == class_id
    ]

    users_sorted = sorted(
        users,
        key=lambda x: next(
            (record["booked_at"] for record in bookings if record["user_email"]
             == x["user_email"] and record["class_id"] == class_id),
            ""
        ),
        reverse=True
    )
    return users_sorted
