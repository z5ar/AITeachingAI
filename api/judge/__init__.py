from fastapi import APIRouter

router = APIRouter(prefix='/judge', tags=['批改答案API'])

__all__ = ('router', )