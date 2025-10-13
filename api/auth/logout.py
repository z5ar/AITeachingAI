from fastapi import APIRouter, Cookie
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import SessionID
from api import ResponseBaseTable
router = APIRouter()


class LogoutResponse(ResponseBaseTable):
    pass


class LogoutStatus(Enum):
    success = LogoutResponse(code=0, msg='Successfully logged out.')
    invalid = LogoutResponse(code=1, msg='Not logged in yet.')


LogoutResponse.model_config = getattr(LogoutResponse, 'model_config', {})
LogoutResponse.model_config.setdefault('json_schema_extra', {})['examples'] = [
    {'code': s.value.code, 'msg': s.value.msg} for s in LogoutStatus
]


@router.post('/logout', summary='用户登出', description='退出登录，而非删除账户，使用浏览器Cookie实现，无需前端主动传递数据')
def user_logout(UUSessionID: Annotated[str|None, Cookie()] = None) -> LogoutResponse:
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