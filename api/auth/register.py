from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User
from fastapi import APIRouter
from . import UserBaseTable
import bcrypt

router = APIRouter()

class RegisterStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully registered. '}
    existed = {'code': 1, 'msg': 'User existed.'}


class RegisterTable(UserBaseTable):
    pass

@router.post('/register', summary='用户注册', description='使用用户名、昵称和密码，后端不对输入数据做长度校验和用户名唯一性以外的任何校验，请前端实现其余校验。')
def user_register(req: RegisterTable):
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
