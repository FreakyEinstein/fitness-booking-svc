from fastapi import APIRouter, Form

from ..services.users_service import register_user, authenticate_user

router = APIRouter()


print("Hello, I'm in auth.py")


@router.post("/signup")
async def user_signup(
    name: str = Form(..., description="Full name of the user"),
    email: str = Form(..., description="User email address"),
    password: str = Form(..., description="Password (min 8 characters)"),
    client_id: str = Form(
        "user", description="Client type (default: user) can choose between `user` and `instructor` ")
):
    """
    Register a new user.

    - **name**: Full name of the user
    - **email**: User email address
    - **password**: Password (min 8 characters)
    - **client_id**: Choose between a `user` and `instructor`
    """
    return register_user(
        user_name=name,
        user_email=email,
        user_password=password,
        role=client_id
    )


@router.post("/login")
async def login(
    username: str = Form(..., description="User email address"),
    password: str = Form(..., description="Password"),
    client_id: str = Form(
        "user", description="Client type (default: user) can choose between `user` and `instructor` ")
):
    """
    Login and get JWT token.

    - **username**: User email address
    - **password**: Password
    - **client_id**: Choose between a `user` and `instructor`
    """
    return authenticate_user(user_email=username, user_password=password)
