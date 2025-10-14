from fastapi import APIRouter, Cookie
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import SessionID
from pydantic import BaseModel
router = APIRouter()

class LogoutStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully logged out.'}
    invalid = {'code': 1, 'msg': 'Not logged in yet.'}

class LogoutResponse(BaseModel):
    status: LogoutStatus

@router.post('/logout', summary='用户登出', description='退出登录，而非删除账户，使用浏览器Cookie实现，无需前端主动传递数据')
def user_logout(UUSessionID: Annotated[str|None, Cookie()] = None) -> LogoutResponse:
    if not UUSessionID:
        return LogoutResponse(status=LogoutStatus.invalid)
    with Session(dbengine) as sss:
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == UUSessionID)
        res = query.first()
        query.delete()
        sss.commit()
    if (not res) or (res.expired_at <= datetime.now()):
        return LogoutResponse(status=LogoutStatus.invalid)
    return LogoutResponse(status=LogoutStatus.success)