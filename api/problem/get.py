from fastapi import APIRouter
from pydantic import BaseModel, JsonValue
from enum import Enum
from utils import dbengine
from utils.database import Problem
from utils.database.problem_model import ProblemType
from sqlalchemy.orm import Session

router = APIRouter()

class GetProblemRequest(BaseModel):
    problem_id: list[int]

class GetProblemStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully fetched.'}

class ProblemContent(BaseModel):
    id: int
    ptype: ProblemType
    problem: str
    arms: JsonValue
    answer: JsonValue

class GetProblemResponse(BaseModel):
    status: GetProblemStatus
    content: list[ProblemContent|None]

@router.post('/get', summary='获取问题')
def get_problem(req: GetProblemRequest) -> GetProblemResponse:
    if(isinstance(req.problem_id, int)):
        req.problem_id = [req.problem_id, ]
    ret: list[ProblemContent] = list()
    with Session(dbengine) as sss:
        for pid in req.problem_id:
            res = sss.query(Problem)\
                .filter(Problem.id == pid)\
                .first()
            if not res:
                ret.append(None)
            else:
                ret.append(ProblemContent(
                    id=res.id,
                    ptype=res.ptype,
                    problem=res.problem,
                    arms=res.arms,
                    answer=res.answer
                ))
    return GetProblemResponse(status=GetProblemStatus.success, content=ret)