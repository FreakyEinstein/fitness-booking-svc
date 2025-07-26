from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.USER

    @field_validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be blank")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password should be atleast 8 characters")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password should be atleast 8 characters")
        return value
