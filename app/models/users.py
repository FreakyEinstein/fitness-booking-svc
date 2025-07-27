from pydantic import BaseModel, EmailStr, field_validator, Field
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    INSTRUCTOR = "instructor"


class UserSignup(BaseModel):
    """
    User signup request.

    - `role` is always "user" for signups.
    """
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password (min 8 characters)")
    role: Role = Field(Role.USER, description="User role (default: user)")

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
    """
    User login request.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password (min 8 characters)")

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password should be atleast 8 characters")
        return value
