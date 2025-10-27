from fastapi import APIRouter, Cookie
from . import UserBaseRequest
from typing import Annotated
from pydantic import BaseModel, Field
from enum import Enum
from utils.auth import get_userid_with_sessionid
from utils.database import User, SessionID
from sqlalchemy.orm import Session
from utils import dbengine
from datetime import datetime
import bcrypt

router = APIRouter()

class RepasswdRequest(UserBaseRequest):
    new_passwd: Annotated[str, Field(min_length=8, max_length=32, description='密码明文，区分大小写')] 

class RepasswdStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully changed password.'}
    invalid = {'code': 1, 'msg': 'Invalid password.'}
    offline = {'code': 2, 'msg': 'Not logged in yet.'}

class RepasswdResponse(BaseModel):
    status: RepasswdStatus

@router.post('/repasswd', summary='修改密码')
def change_password(
    req: RepasswdRequest,
    UUSessionID: Annotated[str|None, Cookie()] = None
) -> RepasswdResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        return RepasswdResponse(status=RepasswdStatus.offline)
    
    with Session(dbengine) as sss:
        query = sss\
            .query(User)\
            .filter(User.id == user_id)
        res = query.first()
        
        if res.username != req.username:
            return RepasswdResponse(status=RepasswdStatus.invalid)
        if not bcrypt.checkpw(req.passwd.encode(), res.passwd_hash):
            return RepasswdResponse(status=RepasswdStatus.invalid)
        
        salt = bcrypt.gensalt()
        passwd_hash = bcrypt.hashpw(req.new_passwd.encode(), salt)

        sss.query(SessionID)\
            .filter(SessionID.user_id == res.id)\
            .delete()
        query.update({User.passwd_hash: passwd_hash})
        sss.commit()
    return RepasswdResponse(status=RepasswdStatus.success)