from datetime import datetime
import pytz
import requests
from fastapi import Request

from ..config import Settings

settings = Settings()
APP_TIMEZONE = pytz.timezone(settings.app_timezone)


def parse_iso_datetime(dt: str) -> datetime:
    """Parse ISO string to aware datetime (UTC if no tzinfo)."""
    dt_obj = datetime.fromisoformat(dt)
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=pytz.UTC)
    return dt_obj


def to_local(dt: datetime, tz_str: str = None) -> datetime:
    """Convert aware datetime to local timezone (default app timezone)."""
    tz = pytz.timezone(tz_str) if tz_str else APP_TIMEZONE
    return dt.astimezone(tz)


def to_local_str(dt: datetime, tz_str: str = None, fmt: str = "%d-%m-%Y %H:%M") -> str:
    """Convert aware datetime to local timezone and format as string."""
    return to_local(dt, tz_str).strftime(fmt)


def convert_utc_to_local(dt: str, client_timezone=None) -> str:
    """Convert UTC ISO string to local time string."""
    dt_obj = parse_iso_datetime(dt)
    return to_local_str(dt_obj, client_timezone)


def get_timezone_from_ip(request: Request):
    try:
        ip_address = request.client.host
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        data = response.json()
        if 'timezone' in data:
            return data['timezone']
        else:
            return None
    except requests.exceptions.RequestException:
        return None

# Deprecated: Use app/utils/timezone_utils.py for all timezone and datetime handling.
