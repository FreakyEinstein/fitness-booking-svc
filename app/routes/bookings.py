from fastapi import APIRouter, Depends, HTTPException

from ..utils.jwt import get_current_user
from ..models.booking import Booking
from ..services.booking_service import book_class, get_bookings_by_user_email, get_class_booked_users
from ..utils.classes import get_timezone_from_ip

router = APIRouter()


@router.post("")
async def book_a_class(
    booking: Booking,
    token=Depends(get_current_user),
    timezone=Depends(get_timezone_from_ip)
):
    """
    Book a class.

    - **class_id**: ID of the class to book
    """
    return book_class(token, booking, timezone)


@router.get("/bookings/me")
async def retrieve_my_bookings(
    class_id: str = None,
    token=Depends(get_current_user),
    timezone=Depends(get_timezone_from_ip)
):
    """
    Get all bookings for the current user/instructor.
    If the user is an instructor, return the list of all the students who booked the classes created by the instructor.

    - **class_id**: ***Mandatory*** if the token is of intructor.
    - **timezone**: (optional) Timezone string (e.g. "Asia/Kolkata"). If not provided, uses IP-based or default.
    """
    if token["role"] == "user":
        return get_bookings_by_user_email(token["email"], timezone)
    elif token["role"] == "instructor" and class_id:
        return get_class_booked_users(token, class_id)
    else:
        raise HTTPException(400, "Bad Request")
