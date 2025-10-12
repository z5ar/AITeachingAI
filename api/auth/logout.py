from fastapi import APIRouter, Cookie
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import SessionID

router = APIRouter()

class LogoutStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully logged out.'}
    invalid = {'code': 1, 'msg': 'Not logged in yet.'}


@router.post('/logout', summary='用户登出', description='退出登录，而非删除账户')
def user_logout(UUSessionID: Annotated[str|None, Cookie()] = None):
    if not UUSessionID:
        return LogoutStatus.invalid
    with Session(dbengine) as sss:
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == UUSessionID)
        res = query.first()
        query.delete()
        sss.commit()
    if (not res) or (res.expired_at <= datetime.now()):
        return LogoutStatus.invalid
    return LogoutStatus.success