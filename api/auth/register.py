from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User
from fastapi import APIRouter
from . import UserBaseRequest
import bcrypt
from api import ResponseBaseTable

router = APIRouter()


class RegisterResponse(ResponseBaseTable):
    pass


class RegisterStatus(Enum):
    success = RegisterResponse(code=0, msg='Successfully registered. ')
    existed = RegisterResponse(code=1, msg='User existed.')


RegisterResponse.model_config = getattr(RegisterResponse, 'model_config', {})
RegisterResponse.model_config.setdefault('json_schema_extra', {})['examples'] =[
    {'code': s.value.code, 'msg': s.value.msg} for s in RegisterStatus
]


class RegisterRequest(UserBaseRequest):
    pass

@router.post('/register', summary='用户注册', description='''\
请求体包含用户名和密码。
后端不对输入数据做长度校验和用户名唯一性以外的任何校验。
前端需要实现的其余校验有：
1. 用户名合规性检验：只含字母、数字和下划线，且不以数字开头。
2. 强密码检验：至少包含大写字母、小写字母、数字、符号的至少三种。
''')
def user_register(req: RegisterRequest) -> RegisterResponse:
    with Session(dbengine) as sss:
        res = sss\
            .query(User)\
            .filter(User.username == req.username)\
            .filter(User.deleted_at == None)\
            .count()
        if res:
            return RegisterStatus.existed
        salt = bcrypt.gensalt()
        passwd_hash = bcrypt.hashpw(req.passwd.encode(), salt)
        sss.add(User(
            username=req.username,
            passwd_hash=passwd_hash,
            created_at=datetime.now()
        ))
        sss.commit()
    return RegisterStatus.success
