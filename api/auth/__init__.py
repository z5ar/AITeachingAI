from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Annotated

_examples = [
    {'username': "tadokoro_kouji", "passwd": "ikusgiaaa114514"},
    {"username": "abc123", "passwd": "Thisisapasswd"}
]

class UserBaseRequest(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=32, description='用户名，或者说账号，必须由字母、数字和下划线组成，且不能数字开头，区分大小写', examples=['hustseee', 'abc123', '_114514'])]
    passwd: Annotated[str, Field(min_length=8, max_length=32, description='密码明文，区分大小写')] 

    model_config = {
        'json_schema_extra': {
            'examples': _examples
        }
    }

from .login import router as lirouter
from .logout import router as lorouter
from .register import router as regrouter
from .unregister import router as unregrouter

router = APIRouter(prefix='/auth', tags=['身份认证API'])
router.include_router(lirouter)
router.include_router(lorouter)
router.include_router(regrouter)
router.include_router(unregrouter)

__all__ = ('router', )