from fastapi import APIRouter, Cookie
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import SessionID, LearningProgress, User
from . import ProgressBaseModel

router = APIRouter()

class ProgressModel(ProgressBaseModel):
    started_at: Annotated[datetime, Field(description='初次学习的时间')]

class ProgressStatus(Enum):
    success = {'code':0, 'msg':'Successfully got.'}
    offline = {'code':1, 'msg':'Not logged in yet.'}

class ProgressResponse(BaseModel):
    status: ProgressStatus
    progress: ProgressModel|None = None

@router.get('/{section_id}/get', summary='获取学习进度', description='获取某一节的学习进度，需要`section_id`，`user_id`通过浏览器Cookie获取无需前端传递。')
def get_progress(
    section_id: int, 
    UUSessionID: Annotated[
        str | None, 
        Cookie()
    ] = None
):
    with Session(dbengine) as sss:
        if not UUSessionID:
            return ProgressResponse(status=ProgressStatus.offline)
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == UUSessionID)
        res = query.first()
        if not res:
            return ProgressResponse(status=ProgressStatus.offline)
        if res.expired_at <= datetime.now():
            query.delete()
            return ProgressResponse(status=ProgressStatus.offline)
        user_id = res.user_id

        query = sss.query(LearningProgress)\
            .where(LearningProgress.section_id == section_id)\
            .where(LearningProgress.user_id == user_id)
        if query.count():
            res = query.first()
            return ProgressResponse(
                status=ProgressStatus.success, 
                progress=ProgressModel(
                    section_id=section_id,
                    user_id=user_id,
                    percentage=res.percentage,
                    time_spent=res.time_spent,
                    started_at=res.started_at,
                    completed_at=res.completed_at
                )
            )
    return ProgressResponse(status=ProgressStatus.success)