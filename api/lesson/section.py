from fastapi import APIRouter
from utils import dbengine
from utils.database import CourseSection as Section
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, JsonValue
from typing import Annotated
from enum import Enum
router = APIRouter(prefix='/section')

class SectionModel(BaseModel):
    id: Annotated[int, Field(description='为每一小节分配的ID')]
    course_id: Annotated[int, Field(description='该小节所属课程的ID')]
    order: Annotated[int, Field(description='该小节在该课程中的顺序号')]
    title: Annotated[str, Field(description='标题')]
    content: Annotated[JsonValue, Field(description='')]
    
    model_config = {
        'json_schema_extra': {
            'examples':[{
                "id": 1, "course_id": 1, "order": 1,
                "title": "Chapter 1: 给公猪做产后护理分几步？",
                "content": ""
            },{
                "id": 2, "course_id": 1, "order": 2,
                "title": "1-1 把猪圈门打开",
                "content": ""
            },{
                "id": 3, "course_id": 1, "order": 3,
                "title": "1-2 给猪做护理",
                "content": ""
            },{
                "id": 4, "course_id": 1, "order": 4,
                "title": "1-3 把猪圈门关上",
                "content": ""
            }]
        }
    }

class SectionStatus(Enum):
    success = {'code':0, 'msg': 'Successfully got.'}

class SectionResponse(BaseModel):
    status: SectionStatus
    sections: list[SectionModel] | None = None

@router.get('/{course_id}/getAll', summary='获取课程小节')
def get_section_list(course_id: int) -> SectionResponse:
    ret: list[SectionModel] = list()
    with Session(dbengine) as sss:
        res = sss.query(Section)\
            .filter(Section.course_id == course_id)\
            .all()
        for item in res:
            ret.append(SectionModel(
                id=item.id,
                course_id=item.course_id,
                order=item.order,
                title=item.title,
                content=item.content
            ))
    return SectionResponse(status=SectionStatus.success, sections=ret)