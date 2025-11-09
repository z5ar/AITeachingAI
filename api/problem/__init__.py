from fastapi import APIRouter

router = APIRouter(prefix='/problem', tags=['问题相关API'])


from .get import router as getrouoter
from .judge import router as judgerouter
router.include_router(getrouoter)
router.include_router(judgerouter)

__all__ = ('router', )