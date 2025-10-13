from fastapi import APIRouter

from .course import router as course_router
router = APIRouter(prefix='/lesson', tags=['课程相关API'])
router.include_router(course_router)

__all__ = ('router', )