from fastapi import APIRouter

from .auth import router as auth_router
from .classes import router as classes_router
from .bookings import router as bookings_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(classes_router, prefix="/classes", tags=["Classes"])
router.include_router(bookings_router, prefix="/book", tags=["Bookings"])
