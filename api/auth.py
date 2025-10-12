from fastapi import APIRouter, Query
from enum import Enum
from datetime import datetime
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User

router = APIRouter(prefix='/api/auth')

class RegisterStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully registered. '}
    existed = {'code': 1, 'msg': 'User existed.'}
    internal = {'code': 2, 'msg': 'Internal error.'}
@router.post('/register', summary='用户注册', description='后端不对输入数据做长度校验和用户名唯一性以外的任何校验，请前端实现其余校验。')
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
        sss.add(User(
            username=username,
            nickname=nickname,
            passwd_hash=passwd,
            created_at=datetime.now()
        ))
        try:
            sss.commit()
        except IntegrityError:
            return RegisterStatus.internal
    return RegisterStatus.success