from pydantic import ValidationError
from fastapi import HTTPException
from pathlib import Path
import json
import bcrypt

from ..models.users import UserSignup
from ..utils.jwt import create_access_token

from ..config import Settings

USERS_FILE = Path("app/storage/users.json")

settings = Settings()


def get_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def get_user_by_email(email):
    users = get_users()
    return next((u for u in users if u["email"] == email), None)


def register_user(user_name: str, user_email: str, user_password: str, role: str = "user"):
    try:
        if role == "admin":
            raise HTTPException(403, detail="Cannot register as an admin")

        # validate the payload
        user = UserSignup(
            name=user_name,
            email=user_email,
            password=user_password,
            role=role
        )

        # check for duplicate user entry
        existing = get_user_by_email(email=user_email)
        if existing:
            raise HTTPException(status_code=403, detail="User already exists")

        # hash the password
        hashed_password = bcrypt.hashpw(
            user_password.encode(), bcrypt.gensalt()).decode()

        # save the user
        users = get_users()
        users.append({
            "name": user_name,
            "email": user_email,
            "password": hashed_password,
            "role": role
        })

        save_users(users)

    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=[{k: v if k != "loc" else v[0] for k, v in err.items() if k != 'ctx' and k != "type"}
                    for err in e.errors(include_url=False)]
        )

    return {"success": True, "detail": f"{role.upper()} signed up successfully"}


def authenticate_user(user_email: str, user_password: str):
    user = get_user_by_email(user_email)

    if not user:
        return HTTPException(status_code=404, detail="Incorrect Credentials")

    # verify password
    if not bcrypt.checkpw(user_password.encode(), user["password"].encode()):
        return HTTPException(status_code=401, detail="Incorrect Credentials")

    # create a jwt token
    del user["password"]  # exclude password in the jwt token
    token = create_access_token(user)

    return {"success": True, "access_token": token}
