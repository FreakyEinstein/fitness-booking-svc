from fastapi import APIRouter, Form

from ..services.users_service import register_user, authenticate_user

router = APIRouter()


@router.post("/signup")
async def user_signup(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    return register_user(
        user_name=name,
        user_email=email,
        user_password=password
    )


@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...), client_id: str = Form("USER")):
    return authenticate_user(user_email=username, user_password=password)
