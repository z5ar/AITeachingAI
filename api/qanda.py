# 模块名含义：Q&A
from fastapi import APIRouter
from pydantic import BaseModel
from enum import Enum

router = APIRouter(prefix='/qanda', tags=['答疑API'])

class QAndARequest(BaseModel):
    pass

class QAndAStatus(Enum):
    pass

class QAndAResponse(BaseModel):
    status: QAndAStatus
    content: str|None = None

@router.post('/', summary='由AI答疑', description='我暂时想不太明白该使用什么参数，返回什么值，待交流后实现')
def qanda(
    req: QAndARequest
) -> QAndAResponse:
    pass