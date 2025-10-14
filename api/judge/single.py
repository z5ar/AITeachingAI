from fastapi import APIRouter
from pydantic import BaseModel, JsonValue
from utils import dbengine
from utils.database import Problem
from utils.database.problem_model import ProblemType
from sqlalchemy.orm import Session
from enum import Enum
import utils.ai

router = APIRouter()

class SingleJudgmentRequest(BaseModel):
    problem_id: int
    answer: str|list[str]|None

class SingleJudgmentScore(BaseModel):
    std: JsonValue|None
    score: int
    mscore: int
    comment: str|None = None

class SingleJudgmentStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully judged.'}
    invalid = {'code': 1, 'msg': 'Invalid problem id.'}
    aierror = {'code': 2, 'msg': 'Failed to fetch result from AI.'}

class SingleJudgmentResponse(BaseModel):
    status: SingleJudgmentStatus
    result: SingleJudgmentScore|None = None

@router.post('/single')
def judge_single(req: SingleJudgmentRequest):
    with Session(dbengine) as sss:
        query = sss.query(Problem)\
            .filter(Problem.id == req.problem_id)
        if not query.count():
            return SingleJudgmentResponse(status=SingleJudgmentStatus.invalid)
        prob = query.first()
    ret = {'std':prob.answer}
    if prob.ptype in (ProblemType.single_choice, ProblemType.blank_filling):
        ret['mscore'] = 1
        ret['score'] = 1 if req.answer.strip() in prob.answer else 0
    elif prob.ptype in (ProblemType.multiple_choice, ProblemType.variable_choice):
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
    return SingleJudgmentScore(**ret)

