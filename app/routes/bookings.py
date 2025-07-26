from fastapi import APIRouter, Depends

from ..utils.jwt import get_current_user
from ..services.booking_service import book_class, get_bookings_by_user_email

router = APIRouter()


@router.post("/book")
async def book_a_class(token=Depends(get_current_user)):
    return book_class(token["email"])


@router.get("/bookings")
async def get_all_bookings(token=Depends(get_current_user)):
    return get_bookings_by_user_email(token["email"])
