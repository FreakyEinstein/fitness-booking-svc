from datetime import datetime
import pytz
import requests
from fastapi import Request

from ..config import Settings

settings = Settings()
APP_TIMEZONE = settings.app_timezone


def get_timezone(tz_str: str = None):
    """
    Return pytz timezone object from string or default app timezone.
    """
    return pytz.timezone(tz_str) if tz_str else pytz.timezone(APP_TIMEZONE)


def parse_ist_iso_to_utc_iso(ist_iso_str: str) -> str:
    """
    Parse an ISO string in IST (Asia/Kolkata) and return a UTC ISO string.
    Example input: "2025-07-28T05:30:00"
    """
    ist = pytz.timezone("Asia/Kolkata")
    dt = datetime.fromisoformat(ist_iso_str)
    if dt.tzinfo is None:
        dt = ist.localize(dt)
    else:
        dt = dt.astimezone(ist)
    dt_utc = dt.astimezone(pytz.UTC)
    return dt_utc.isoformat()


def parse_utc_iso_to_local_str(utc_iso_str: str, tz_str: str = None, fmt: str = "%d-%m-%Y %H:%M") -> str:
    """
    Convert a UTC ISO string to a local time string in the given timezone.
    """
    tz = get_timezone(tz_str)
    dt_utc = datetime.fromisoformat(utc_iso_str)
    if dt_utc.tzinfo is None:
        dt_utc = pytz.UTC.localize(dt_utc)
    dt_local = dt_utc.astimezone(tz)
    return dt_local.strftime(fmt)


def parse_utc_iso_to_local_iso(utc_iso_str: str, tz_str: str = None) -> str:
    """
    Convert a UTC ISO string to a local ISO string in the given timezone.
    """
    tz = get_timezone(tz_str)
    dt_utc = datetime.fromisoformat(utc_iso_str)
    if dt_utc.tzinfo is None:
        dt_utc = pytz.UTC.localize(dt_utc)
    dt_local = dt_utc.astimezone(tz)
    return dt_local.isoformat()


def get_timezone_from_ip(request: Request):
    """
    Get the timezone string (e.g. "Asia/Kolkata") from the client's IP address.
    Falls back to app default timezone if not available.
    """
    try:
        ip_address = request.client.host
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        data = response.json()
        if 'timezone' in data:
            return data['timezone']
        else:
            return APP_TIMEZONE
    except Exception:
        return APP_TIMEZONE
