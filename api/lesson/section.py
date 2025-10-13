from fastapi import APIRouter
from utils import dbengine
from utils.database import CourseSection as Section
from sqlalchemy.orm import Session
router = APIRouter(prefix='/section')

@router.get('/{course_id}/getAll', summary='获取课程小节')
def get_section_list(course_id: int):
    ret: list[dict] = list()
    with Session(dbengine) as sss:
        res = sss.query(Section)\
            .filter(Section.course_id == course_id)\
            .all()
        for item in res:
            ret.append({
                'id': item.id,
                'course_id': item.course_id,
                'order': item.order,
                'title': item.title,
                'type': item.content_type
            })
    return ret