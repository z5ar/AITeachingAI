from .get import router as getrouter
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

class ProgressBaseModel(BaseModel):
    section_id: int
    user_id: int
    percentage: Annotated[float, Field(description='学习进度百分比，不带百分号的百分数')]
    time_spent: Annotated[int, Field(description='已学时间，单位秒')]
    completed_at: datetime|None = None

router = APIRouter(prefix='/progress')
router.include_router(getrouter)

__all__ = ('router', )