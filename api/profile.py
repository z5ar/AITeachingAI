from fastapi import APIRouter, Cookie
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from utils.auth import get_userid_with_sessionid
from sqlalchemy.orm import Session
from utils import dbengine
from utils.database import User, Profile
from utils.database.profile_model import ThemeColour
from typing import Annotated
from utils.avatar import get_identicon
from hashlib import md5
from pathlib import Path

PATH_AVATAR = Path(__file__).parents[1] / 'data' / 'avatar'
PATH_AVATAR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix='/profile', tags=['个人信息API'])
class ProfileBase(BaseModel):
    nickname: str|None = None
    avatar: str|None = None
    colour: ThemeColour|None = None

class WhoamiStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully fetched.'}
    offline = {'code': 1, 'msg': 'Not logged in.'}

class IamwhoStatus(Enum):
    success = {'code': 0, 'msg': 'Successfully modified.'}
    offline = {'code': 1, 'msg': 'Not logged in.'}

class WhoamiResponse(ProfileBase):
    status: WhoamiStatus
    username: str|None = None
    user_id: int|None = None
    logged_in_at: datetime|None = None

class IamwhoResponse(BaseModel):
    status: IamwhoStatus

class IamwhoRequest(ProfileBase):
    pass

@router.get('/whoami', summary='获取个人信息')
def whoami(UUSessionID: str | None = Cookie(None)) -> WhoamiResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        return WhoamiResponse(status=WhoamiStatus.offline)
    with Session(dbengine) as sss:
        user = sss.query(User).filter(User.id == user_id).first()
        qprof = sss.query(Profile).filter(Profile.id == user_id)
        prof = qprof.first()
        flag = False
        if not qprof.count():
            prof = Profile(id=user_id)
            sss.add(prof)
            sss.commit()
            prof = qprof.first()
        if not prof.nickname:
            prof.nickname = '蒟蒻12138'
            flag = True
        if not prof.avatar:
            filename = (md5(f'{user_id}_{prof.nickname}'.encode()).hexdigest() + '.webp')
            ok = get_identicon(prof.nickname, PATH_AVATAR / filename)
            if ok:
                prof.avatar = filename
                flag = True
        if not prof.colour:
            prof.colour = ThemeColour.blue
            flag = True
        if flag:
            qprof.update({
                Profile.id: user_id,
                Profile.avatar: prof.avatar,
                Profile.nickname: prof.nickname,
                Profile.colour: prof.colour
            })
            sss.commit()
        return WhoamiResponse(
            status=WhoamiStatus.success,
            username=user.username,
            user_id=user_id,
            nickname=prof.nickname,
            avatar=prof.avatar,
            colour=prof.colour,
            logged_in_at=user.logged_in_at
        )

@router.post('/iamwho', summary='更改个人信息')
def iamwho(
    UUSessionID: Annotated[str|None, Cookie()],
    req: IamwhoRequest
) -> IamwhoResponse:
    user_id = get_userid_with_sessionid(UUSessionID)
    if user_id == -1:
        return IamwhoResponse(status=IamwhoStatus.offline)
    with Session(dbengine) as sss:
        prof = sss.query(Profile).filter(Profile.id == user_id)
        if prof.count():
            to_modify = dict()
            if req.nickname:
                to_modify[Profile.nickname] = req.nickname
            if req.avatar:
                to_modify[Profile.avatar] = req.avatar
            if req.colour:
                to_modify[Profile.colour] = req.colour
            prof.update(to_modify)
        else:
            sss.add(Profile(
                id=user_id,
                avatar=req.avatar,
                nickname=req.nickname,
                colour=req.colour
            ))
        sss.commit()
    return IamwhoResponse(status=IamwhoStatus.success)