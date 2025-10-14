from fastapi import APIRouter, Cookie
from pydantic import BaseModel, Field, JsonValue
from typing import Annotated
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import SessionID, LearningProgress, User
from utils.auth import get_userid_with_sessionid

router = APIRouter(prefix='/progress')


class ProgressBaseModel(BaseModel):
    percentage: Annotated[float, Field(description='学习进度百分比，不带百分号的百分数')]
    time_spent: Annotated[int, Field(description='已学时间，单位秒')]
    completed_at: datetime|None = None
    draft: JsonValue|None = None

    model_config = {
        'json_schema_extra': {
            'examples':[{
                'percentage': 45.45,
                'time_spent': 114514,
                'completed_at': None,
                'draft': dict()
            },{
                'percentage': 100,
                'time_spent': 1_919_810,
                'completed_at': datetime(2025,10,10,10,10,10,101010),
                'draft': dict()
            }]
        }
    }


class GetProgressModel(ProgressBaseModel):
    section_id: int
    user_id: int
    started_at: Annotated[datetime, Field(description='初次学习的时间')]

    model_config = {
        'json_schema_extra':{
            'examples':[{
                'user_id': 114514,
                'section_id': 1919810,
                'started_at': datetime.now(),
                'percentage': 45.45,
                'time_spent': 114514,
                'completed_at': None
            }]
        }
    }

class GetProgressStatus(Enum):
    success = {'code':0, 'msg':'Successfully got.'}
    offline = {'code':1, 'msg':'Not logged in yet.'}


class GetProgressResponse(BaseModel):
    status: GetProgressStatus
    progress: GetProgressModel|None = None


@router.get('/{section_id}/get', summary='取学习进度', description='获取某一节的学习进度，需要`section_id`，`user_id`通过浏览器Cookie获取无需前端传递。')
def get_progress(
    section_id: int, 
    UUSessionID: Annotated[
        str | None, 
        Cookie()
    ] = None
) -> GetProgressResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        return GetProgressResponse(status=GetProgressStatus.offline)
    
    with Session(dbengine) as sss:
        query = sss.query(LearningProgress)\
            .where(LearningProgress.section_id == section_id)\
            .where(LearningProgress.user_id == user_id)
        if query.count():
            res = query.first()
            return GetProgressResponse(
                status=GetProgressStatus.success, 
                progress=GetProgressModel(
                    section_id=section_id,
                    user_id=user_id,
                    percentage=res.percentage,
                    time_spent=res.time_spent,
                    started_at=res.started_at,
                    completed_at=res.completed_at
                )
            )
    return GetProgressResponse(status=GetProgressStatus.success)


class SetProgressModel(ProgressBaseModel):
    pass


class SetProgressStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully updated.'}
    offline = {'code': 1, 'msg': 'Not logged in yet.'}

class SetProgressResponse(BaseModel):
    status: SetProgressStatus


@router.post('/{section_id}/set', summary='置学习进度')
def set_progress(
    section_id:int,
    UUSessionID: Annotated[str, Cookie()], 
    new_progress:SetProgressModel
) -> SetProgressResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        return SetProgressResponse(status=SetProgressStatus.offline)
    
    with Session(dbengine) as sss:
        query = sss.query(LearningProgress)\
            .where(LearningProgress.section_id == section_id)\
            .where(LearningProgress.user_id == user_id)
        if query.count():
            query.update({
                LearningProgress.percentage: new_progress.percentage,
                LearningProgress.time_spent: new_progress.time_spent,
                LearningProgress.completed_at: new_progress.completed_at,
                LearningProgress.draft: new_progress.draft
            })
        else:
            sss.add(
                LearningProgress(
                    section_id=section_id,
                    user_id=user_id,
                    percentage=new_progress.percentage,
                    time_spent=new_progress.time_spent,
                    completed_at=new_progress.completed_at,
                    draft=new_progress.draft
                )
            )
        sss.commit()
    return SetProgressResponse(status=SetProgressStatus.success)

