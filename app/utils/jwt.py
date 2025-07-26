import jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..config import Settings

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data):
    data["exp"] = datetime.now(UTC) + \
        timedelta(minutes=settings.jwt_expiry_in_hours)

    token = jwt.encode(data, key=settings.jwt_secret_key,
                       algorithm=settings.jwt_algorithm)

    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key,
                             algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        token = jwt.decode(token, settings.jwt_secret_key,
                           [settings.jwt_algorithm])
        return token
    except Exception as _:
        raise HTTPException(status_code=403, detail="Not Authorized")


def parse_admin_token(token: str = Depends(oauth2_scheme)):
    try:
        token = jwt.decode(token, settings.jwt_secret_key,
                           [settings.jwt_algorithm])
        if token["role"] != "ADMIN":
            raise HTTPException(status_code=403, detail="Forbidden")
        return token
    except Exception as _:
        raise HTTPException(status_code=403, detail="Not Authorized")
