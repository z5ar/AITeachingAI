from fastapi import APIRouter, Cookie
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User, SessionID
from . import UserBaseRequest
import bcrypt
from api import ResponseBaseTable

router = APIRouter()


class UnregisterResponse(ResponseBaseTable):
    pass


class UnregisterStatus(Enum):
    success = UnregisterResponse(code=0, msg='Successfully unregistered.')
    invalid = UnregisterResponse(code=1, msg='Invalid password.')
    offline = UnregisterResponse(code=2, msg='Not logged in yet.')


UnregisterResponse.model_config = getattr(UnregisterResponse, 'model_config', {})
UnregisterResponse.model_config.setdefault('json_schema_extra', {})['examples'] = [
    {'code': s.value.code, 'msg': s.value.msg} for s in UnregisterStatus
]


class UnregisterRequest(UserBaseRequest):
    pass

@router.post('/unregister', summary='注销账户', description='删除账户')
def user_unregister(req: UnregisterRequest, UUSessionID: Annotated[str|None, Cookie()] = None) -> UnregisterResponse:
    userid = None
    if not UUSessionID:
        return UnregisterStatus.offline
    with Session(dbengine) as sss:
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == UUSessionID)
        res = query.first()
        query.delete()
        sss.commit()
        if (not res) or (res.expired_at <= datetime.now()):
            return UnregisterStatus.offline
        userid = res.user_id
    
    with Session(dbengine) as sss:
        query = sss\
            .query(User)\
            .filter(User.id == userid)
        res = query.first()
        
        if res.username != req.username:
            return UnregisterStatus.invalid
        if not bcrypt.checkpw(req.passwd.encode(), res.passwd_hash):
            return UnregisterStatus.invalid
        
        sss.query(SessionID)\
            .filter(SessionID.user_id == res.id)\
            .delete()
        query.update({User.deleted_at: datetime.now()})
        sss.commit()
    return UnregisterStatus.success