from fastapi import APIRouter

from .auth import router as auth_router
from .classes import router as classes_router
from .bookings import router as bookings_router
from .income import router as income_router
from .budget import router as budget_router
from .transactions import router as transactions_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(classes_router, prefix="/classes", tags=["Classes"])
router.include_router(bookings_router, prefix="/book", tags=["Bookings"])

# Financial management routes
router.include_router(income_router, prefix="/income", tags=["Income Sources"])
router.include_router(budget_router, prefix="/budget", tags=["Budget Categories"])
router.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])


print("Hello i'm in routers/__init__.py")
