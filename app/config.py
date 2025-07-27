from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str = "anyrandomstring"
    jwt_algorithm: str = "HS256"
    jwt_expiry_in_hours: int = 6
    app_timezone: str = "Asia/Kolkata"

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()
