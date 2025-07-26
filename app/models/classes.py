from pydantic import BaseModel, field_validator

from datetime import datetime, timedelta, timezone as dt_timezone
import pytz

from ..config import Settings

settings = Settings()
timezone = settings.app_timezone
APP_TIMEZONE = pytz.timezone(timezone)


class Class(BaseModel):
    name: str
    datetime_of_class: str
    instructor: str
    total_slots: int = 10
    available_slots: int

    @field_validator("datetime_of_class", mode="before")
    def convert_ist_string_to_utc_iso(cls, value: str) -> str:
        """
        Convert from IST string format 'DD-MM-YYYY HH:mm' to UTC ISO format string.
        """
        try:
            # Parse the naive datetime
            dt_naive = datetime.strptime(value, "%d-%m-%Y %H:%M")
            # Localize to IST
            dt_ist = APP_TIMEZONE.localize(dt_naive)
            # Convert to UTC
            dt_utc = dt_ist.astimezone(pytz.UTC)
            # Return as ISO string in UTC
            return dt_utc.isoformat()
        except Exception as e:
            raise ValueError(f"Invalid datetime format: {e}")
