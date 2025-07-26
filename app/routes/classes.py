from fastapi import APIRouter, Depends

from ..models.classes import Class
from ..utils.jwt import parse_admin_token
from ..utils.classes import get_timezone_from_ip, convert_utc_to_local

router = APIRouter()


@router.get("")
async def get_all_classes(timezone: str = Depends(get_timezone_from_ip)):
    return


@router.post("")
async def create_class(session_class: Class,
                       # token=Depends(parse_admin_token)
                       ):
    '''
    Input datetime_of_class in the format DD-MM-YYYY HH:mm in IST timezone
    '''
    doc = {k: v for k, v in session_class.__dict__.items() if v is not None}
    doc["datetime_of_class"] = convert_utc_to_local(doc["datetime_of_class"])
    return doc
