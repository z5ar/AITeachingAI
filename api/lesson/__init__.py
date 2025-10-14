from fastapi import APIRouter

from .course import router as course_router
from .section import router as section_router
router = APIRouter(prefix='/lesson', tags=['课程相关API'])
router.include_router(course_router)
router.include_router(section_router)


__all__ = ('router', )