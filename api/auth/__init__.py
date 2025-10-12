from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Annotated

class UserBaseTable(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=32, description='用户名，或者说账号，必须由字母、数字和下划线组成，且不能数字开头，区分大小写')]
    passwd: Annotated[str, Field(min_length=8, max_length=32, description='密码明文，区分大小写')] 

from .login import router as lirouter
from .logout import router as lorouter
from .register import router as regrouter
from .unregister import router as unregrouter

router = APIRouter(prefix='/api/auth')
router.include_router(lirouter)
router.include_router(lorouter)
router.include_router(regrouter)
router.include_router(unregrouter)

__all__ = ('router', )