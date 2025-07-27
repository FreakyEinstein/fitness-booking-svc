from datetime import datetime

from ..config import Settings

settings = Settings()


def convert_utc_iso_to_local_iso(utc_str: str) -> str:
    """Converts UTC ISO string to local timezone ISO string."""
    utc_dt = datetime.fromisoformat(utc_str)
    return utc_dt.isoformat()
    utc_dt = datetime.fromisoformat(utc_str)
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    local_dt = utc_dt.astimezone(APP_TIMEZONE)
    return local_dt.isoformat()
