from fastapi import APIRouter, Cookie
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User, SessionID
from . import UserBaseRequest
from pydantic import BaseModel
import bcrypt

router = APIRouter()

class UnregisterStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully unregistered.'}
    invalid = {'code': 1, 'msg': 'Invalid password.'}
    offline = {'code': 2, 'msg': 'Not logged in yet.'}

class UnregisterResponse(BaseModel):
    status: UnregisterStatus

class UnregisterRequest(UserBaseRequest):
    pass

@router.post('/unregister', summary='注销账户', description='删除账户')
def user_unregister(req: UnregisterRequest, UUSessionID: Annotated[str|None, Cookie()] = None) -> UnregisterResponse:
    userid = None
    if not UUSessionID:
        return UnregisterResponse(status=UnregisterStatus.offline)
    with Session(dbengine) as sss:
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == UUSessionID)
        res = query.first()
        query.delete()
        sss.commit()
        if (not res) or (res.expired_at <= datetime.now()):
            return UnregisterResponse(status=UnregisterStatus.offline)
        userid = res.user_id
    
    with Session(dbengine) as sss:
        query = sss\
            .query(User)\
            .filter(User.id == userid)
        res = query.first()
        
        if res.username != req.username:
            return UnregisterResponse(status=UnregisterStatus.invalid)
        if not bcrypt.checkpw(req.passwd.encode(), res.passwd_hash.encode()):
            return UnregisterResponse(status=UnregisterStatus.invalid)
        
        sss.query(SessionID)\
            .filter(SessionID.user_id == res.id)\
            .delete()
        query.update({User.deleted_at: datetime.now()})
        sss.commit()
    return UnregisterResponse(status=UnregisterStatus.success)