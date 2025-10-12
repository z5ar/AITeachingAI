from fastapi import APIRouter, Query, Response, Cookie
from enum import Enum
from datetime import datetime, timedelta
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils import dbengine, config
from utils.database import User, SessionID
import bcrypt
import secrets

router = APIRouter(prefix='/api/auth')

class RegisterStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully registered. '}
    existed = {'code': 1, 'msg': 'User existed.'}

@router.post('/register', summary='用户注册', description='使用用户名、昵称和密码，后端不对输入数据做长度校验和用户名唯一性以外的任何校验，请前端实现其余校验。')
def user_register(
    username: Annotated[str, Query(min_length=4, max_length=32, description='用户名，或者说账号，必须由字母、数字和下划线组成，且不能数字开头，区分大小写')],
    nickname: Annotated[str, Query(max_length=64, description='昵称')],
    passwd: Annotated[str, Query(min_length=8, max_length=32, description='密码明文')] 
):
    with Session(dbengine) as sss:
        res = sss\
            .query(User)\
            .filter(User.username == username)\
            .filter(User.deleted_at == None)\
            .count()
        if res:
            return RegisterStatus.existed
        salt = bcrypt.gensalt()
        passwd_hash = bcrypt.hashpw(passwd.encode(), salt)
        sss.add(User(
            username=username,
            nickname=nickname,
            passwd_hash=passwd_hash,
            created_at=datetime.now()
        ))
        sss.commit()
    return RegisterStatus.success
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
@router.post('/login', summary='用户登录', description='使用用户名和密码登录')
def user_login(
    username: Annotated[str, Query(description='用户名')],
    passwd: Annotated[str, Query(description='密码')],
    response: Response
):
    with Session(dbengine) as sss:
        res = sss\
            .query(User)\
            .filter(User.username == username)\
            .filter(User.deleted_at == None)\
            .first()
    if not res:
        return LoginStatus.invalid
    if not bcrypt.checkpw(passwd.encode(), res.passwd_hash):
        return LoginStatus.invalid
    with Session(dbengine) as sss:
        sss.query(SessionID)\
            .filter(SessionID.user_id == res.id)\
            .delete()
        sss.commit()
    session_id = _gen_sessionid()
    with Session(dbengine) as sss:
        sss.add(
            SessionID(
                session_id=session_id,
                user_id=res.id,
                expired_at = datetime.now()+timedelta(seconds=config.sessionid.ttl)
            )
        )
        sss.commit()
        response.set_cookie('UUSessionID', session_id, httponly=True)
    return LoginStatus.success

