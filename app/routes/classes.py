from fastapi import APIRouter, Depends

from ..models.classes import Class
from ..services.classes_service import create_new_class, get_classes
from ..utils.jwt import parse_instructor_token
from ..utils.classes import get_timezone_from_ip, convert_utc_to_local

router = APIRouter()


@router.get("")
async def get_all_classes(timezone: str = Depends(get_timezone_from_ip)):
    """
    Get all classes.

    - **timezone**: (optional) Timezone string (e.g. "Asia/Kolkata"). If not provided, uses IP-based or default.
    """
    return get_classes(timezone)


@router.post("")
async def create_class(session_class: Class, token=Depends(parse_instructor_token)):
    """
    Create a new class. Allows the instructor to create a class

    - **datetime_of_class**: Input as IST ISO string (e.g. "2025-07-28T05:30:00")
    - **total_slots**: Total slots available (default: 10)
    - **duration_in_hours**: Duration of class in hours (default: 1)
    """
    return create_new_class(session_class, token)
