from fastapi import APIRouter, Response
from enum import Enum
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from utils import dbengine, config
from utils.database import User, SessionID
from pydantic import BaseModel
from . import UserBaseRequest
import bcrypt
import secrets

router = APIRouter()

def _gen_sessionid():
    with Session(dbengine) as sss:
        sss.query(SessionID)\
            .filter(SessionID.expired_at <= datetime.now())\
            .delete()
        sss.commit()
        session_id = secrets.token_urlsafe(24)
        res = sss\
            .query(SessionID)\
            .filter(SessionID.session_id == session_id)
    if res.count():
        session_id= _gen_sessionid()
    return session_id

class LoginStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully logged in.'}
    invalid = {'code': 1, 'msg': 'Invalid username or password.'}

class LoginResponse(BaseModel):
    status: LoginStatus

class LoginRequest(UserBaseRequest):
    pass

@router.post('/login', summary='用户登录', description='使用用户名和密码登录')
def user_login(
    req: LoginRequest,
    response: Response
) -> LoginResponse:
    userid = None
    with Session(dbengine) as sss:
        query = sss\
            .query(User)\
            .filter(User.username == req.username)\
            .filter(User.deleted_at == None)
        res = query.first()
        
        if not res:
            return LoginResponse(status=LoginStatus.invalid)
        if not bcrypt.checkpw(req.passwd.encode(), res.passwd_hash.encode()):
            return LoginResponse(status=LoginStatus.invalid)
        
        sss.query(SessionID)\
            .filter(SessionID.user_id == res.id)\
            .delete()
        sss.commit()
        userid = res.id
    session_id = _gen_sessionid()
    with Session(dbengine) as sss:
        sss.add(
            SessionID(
                session_id=session_id,
                user_id=userid,
                expired_at = datetime.now()+timedelta(seconds=config.sessionid.ttl)
            )
        )
        sss.commit()
        response.set_cookie('UUSessionID', session_id, httponly=True)
        sss.query(User)\
            .filter(User.id == userid)\
            .update({User.logged_in_at: datetime.now()})
        sss.commit()
    return LoginResponse(status=LoginStatus.success)
