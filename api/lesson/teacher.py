from fastapi import APIRouter, Cookie, Response
from pydantic import BaseModel, JsonValue
from typing import Annotated
from enum import Enum
from utils.ai.teacher import get_teacher, Characters, AITeacher
from utils.auth import get_userid_with_sessionid, gen_sessionid
from utils.config import config
from utils import dbengine
from utils.database import CourseSection as Section
from sqlalchemy.orm import Session


router = APIRouter(prefix='/teacher', tags=['教师API'])

class StartSectionStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully started.'}

class StartSectionResponse(BaseModel):
    status: StartSectionStatus
    first_step: JsonValue

@router.post('/startSection/{section_id}', summary='开始小节')
def start_section(
    section_id: int,
    response: Response,
    UUSessionID: Annotated[str|None, Cookie()] = None
) -> StartSectionResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        UUSessionID = gen_sessionid()
        response.set_cookie('UUSessionID', UUSessionID, httponly=True)
    
    teacher = get_teacher(UUSessionID, Characters.MyCharater, config.ai.token)
    assert isinstance(teacher, AITeacher)

    with Session(dbengine) as sss:
        query = sss.query(Section)\
            .filter(Section.id == section_id)
        res = query.first()
        assert res
        script = res.content

    teacher.load_script(script)
    first = teacher.next_script()
    return StartSectionResponse(status=StartSectionStatus.success, first_step=first)

class NextStepStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully fetched.'}
    initial = {'code': 1, 'msg': 'Not started yet.'}

class NextStepResponse(BaseModel):
    status: NextStepStatus
    content: JsonValue

@router.post('/next_step', summary='下一步')
def next_step(
    UUSessionID: Annotated[str|None, Cookie()] = None
):
    teacher = get_teacher(UUSessionID, Characters.MyCharater, config.ai.token)
    assert isinstance(teacher, AITeacher)
    content = teacher.next_script()
    return NextStepResponse(status=NextStepStatus.success, content=content)

class AnswerQuestionRequest(BaseModel):
    problem: str
    context: int

class AnswerQuestionStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully answered.'}

class AnswerQuestionResponse(BaseModel):
    status: AnswerQuestionStatus
    content: str

@router.post('/answer', summary='回答问题')
def answer_question(
    req: AnswerQuestionRequest,
    UUSessionID: Annotated[str|None, Cookie()] = None
) -> AnswerQuestionResponse:
    teacher = get_teacher(UUSessionID, Characters.MyCharater, config.ai.token)
    assert isinstance(teacher, AITeacher)
    res = teacher.answer_question(question=req.problem,context=req.context)
    return AnswerQuestionResponse(status=AnswerQuestionStatus.success, content=res)

class JudgeRequest(BaseModel):
    problem: str
    std: str|None = None
    ans: str|None = None
    mscore: int

class JudgeStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully judged.'}

class JudgeResponse(BaseModel):
    status: JudgeStatus
    score: int
    comment: str

@router.post('/judge', summary='判定问答题')
def judge(
    req: JudgeRequest,
    UUSessionID: Annotated[str|None, Cookie()] = None
):
    teacher = get_teacher(UUSessionID, Characters.MyCharater, config.ai.token)
    assert isinstance(teacher, AITeacher)

    score, comment = teacher.judge_problem(req.problem, req.std, req.ans, req.mscore)
    return JudgeResponse(status=JudgeStatus.success, score=score, comment=comment)

class GenerateReportRequest(BaseModel):
    time_spent: int
    problems: JsonValue

class GenerateReportStatus(Enum):
    success = {'code': 0, 'msg':'Successfully generated.'}

class GenerateReportResponse(BaseModel):
    status: GenerateReportStatus
    content: JsonValue

@router.post('/report', summary='生成学习报告')
def generate_report(
    req: GenerateReportRequest,
    UUSessionID: Annotated[str|None, Cookie()] = None
):
    teacher = get_teacher(UUSessionID, Characters.MyCharater, config.ai.token)
    assert isinstance(teacher, AITeacher)

    res = teacher.generate_report(req.time_spent, req.problems)
    return GenerateReportResponse(status=GenerateReportStatus.success, content=res)