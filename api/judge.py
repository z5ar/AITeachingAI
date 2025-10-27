from fastapi import APIRouter, Body
from pydantic import BaseModel, JsonValue
from typing import Annotated
from utils import dbengine
from utils.database import Problem
from utils.database.problem_model import ProblemType
from sqlalchemy.orm import Session
from enum import Enum
import utils.ai

router = APIRouter(prefix='/problem', tags=['回答问题API'])

class SingleJudgmentRequest(BaseModel):
    problem_id: int
    answer: str|list[str]|None

class SingleJudgmentScore(BaseModel):
    std: JsonValue|None
    score: int
    mscore: int
    comment: str|None = None
    model_config = {
        'json_schema_extra': {
            'examples': [{
                'std': ['A'],
                'score': 1,
                'mscore': 1,
                'comment': None
            }]
        }
    }

class SingleJudgmentStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully judged.'}
    invalid = {'code': 1, 'msg': 'Invalid problem id.'}
    aierror = {'code': 2, 'msg': 'Failed to fetch result from AI.'}

class SingleJudgmentResponse(BaseModel):
    status: SingleJudgmentStatus
    result: SingleJudgmentScore|None = None

@router.post('/judge', summary='给回答打分')
def judge(
    reqs: Annotated[
        list[SingleJudgmentRequest],
        Body(example=[
            {"problem_id": 1, "answer": ["C"]},
            {"problem_id": 1, "answer": "B"},
            {"problem_id": 2, "answer": "C"},
            {"problem_id": 2, "answer": ["C","A","B"]},
            {"problem_id": 2, "answer": ["A","B"]},
            {"problem_id": 2, "answer": ["C","A","D"]},
            {"problem_id": 3, "answer": "没有意义。"},
            {"problem_id": 4, "answer": ["C","A","B"]}
        ])
    ]
) -> list[SingleJudgmentResponse]:
    retl : list[SingleJudgmentResponse] = list()
    for req in reqs:
        with Session(dbengine) as sss:
            query = sss.query(Problem)\
                .filter(Problem.id == req.problem_id)
            if not query.count():
                retl.append(SingleJudgmentResponse(status=SingleJudgmentStatus.invalid))
                continue
            prob = query.first()
        ret = {'std':prob.answer}
        if prob.ptype in (ProblemType.single_choice, ProblemType.blank_filling):
            if isinstance(req.answer, list):
                req.answer = req.answer[0]
            ret['mscore'] = 1
            ret['score'] = 1 if req.answer.strip() in prob.answer else 0
        elif prob.ptype in (ProblemType.multiple_choice, ProblemType.variable_choice):
            if isinstance(req.answer, str):
                req.answer = [req.answer, ]
            ret['mscore'] = len(prob.answer)
            ret['score'] = 0
            for choice in req.answer:
                if choice not in prob.answer:
                    ret['score'] = 0
                    break
                else:
                    ret['score'] += 1
        else:
            ret['score'], ret['comment'] = utils.ai.judge_answer(req.answer, prob.answer, prob.problem, 700)
            ret['mscore'] = 700
        retl.append(SingleJudgmentResponse(
            status=SingleJudgmentStatus.success,
            result=SingleJudgmentScore(**ret)
        ))
    return retl

class GetProblemRequest(BaseModel):
    problem_id: list[int]

class GetProblemStatus(BaseModel):
    success = {'code': 0, 'msg': 'Successfully fetched.'}

class ProblemContent(BaseModel):
    id: int
    ptype: ProblemType
    problem: str
    answer: JsonValue

class GetProblemResponse(BaseModel):
    status: GetProblemStatus
    content: list[ProblemContent|None]

@router.get('/get', summary='获取问题')
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
                    answer=res.answer
                ))