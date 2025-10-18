from fastapi import APIRouter

from .auth import router as auth_router
from .lesson import router as lesson_router
from .judge import router as judge_router
from .qanda import router as qanda_router

router = APIRouter(prefix='/api')
router.include_router(auth_router)
router.include_router(lesson_router)
router.include_router(judge_router)
router.include_router(qanda_router)

__all__ = ('router', )