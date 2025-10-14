from fastapi import APIRouter
from utils import dbengine
from utils.database import Course
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

router = APIRouter(prefix='/course')
class CourseStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully got.'}

class CourseModel(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'id': 114514,
                    'name': '公猪的产后护理',
                    'description': '拿对书了。',
                    'created_at': datetime(1919,8,10,11,45,14)
                }
            ]
        }
    }
class CourseResponse(BaseModel):
    status: CourseStatus
    courses: list[CourseModel]

@router.get('/getAll', summary='获取课程列表')
def get_course_list() -> CourseResponse:
    ret: list[CourseModel] = list()
    with Session(dbengine) as sss:
        res = sss.query(Course).all()
        for item in res:
            ret.append(CourseModel(
                id=item.id,
                name=item.name,
                description=item.description,
                created_at=item.created_at
            ))
    return CourseResponse(status=CourseStatus.success, courses=ret)