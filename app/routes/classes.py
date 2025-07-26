from fastapi import APIRouter, Depends

from ..models.classes import Class
from ..services.classes_service import create_new_class, get_classes
from ..utils.jwt import parse_admin_token
from ..utils.classes import get_timezone_from_ip, convert_utc_to_local

router = APIRouter()


@router.get("")
async def get_all_classes(timezone: str = Depends(get_timezone_from_ip)):
    return get_classes(timezone)


@router.post("")
async def create_class(session_class: Class, token=Depends(parse_admin_token)):
    '''
    Input datetime_of_class in the format DD-MM-YYYY HH:mm in IST timezone
    '''
    return create_new_class(session_class)
