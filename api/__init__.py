from fastapi import APIRouter

from pydantic import BaseModel
class ResponseBaseTable(BaseModel):
    code: int
    msg: str

from .auth import router as auth_router
from .lesson import router as lesson_router

router = APIRouter(prefix='/api')
router.include_router(auth_router)
router.include_router(lesson_router)

__all__ = ('router', )