from fastapi import APIRouter
from utils import dbengine
from utils.database import Course
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix='/course')

class CourseResponse(BaseModel):
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

@router.get('/getAll', summary='获取课程列表')
def get_course_list() -> list[CourseResponse]:
    ret: list[CourseResponse] = list()
    with Session(dbengine) as sss:
        res = sss.query(Course).all()
        for item in res:
            ret.append(CourseResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                created_at=item.created_at
            ))
    return ret