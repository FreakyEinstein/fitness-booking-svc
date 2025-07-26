from datetime import datetime
import pytz
import requests
from fastapi import Request

from ..config import Settings

settings = Settings()
timezone = settings.app_timezone
APP_TIMEZONE = pytz.timezone(timezone)


def convert_utc_to_local(dt: str, client_timezone) -> str:
    if client_timezone:
        set_timezone = client_timezone
    else:
        set_timezone = APP_TIMEZONE
    dt_utc = datetime.fromisoformat(dt)
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
    dt_local = dt_utc.astimezone(set_timezone)
    return dt_local.strftime("%d-%m-%Y %H:%M")


def get_timezone_from_ip(request: Request):
    try:
        ip_address = request.client.host
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        data = response.json()
        if 'timezone' in data:
            return data['timezone']['id']
        else:
            return None
    except requests.exceptions.RequestException:
        return None
