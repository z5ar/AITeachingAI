from sqlalchemy.orm import Session
from . import dbengine
from datetime import datetime
from .database import SessionID
import secrets

def gen_sessionid():
    with Session(dbengine) as sss:
        sss.query(SessionID)\
            .filter(SessionID.expired_at <= datetime.now())\
            .delete()
        sss.commit()
        session_id = secrets.token_urlsafe(24)
        res = sss\
            .query(SessionID)\
            .filter(SessionID.session_id == session_id)
    if res.count():
        session_id= gen_sessionid()
    return session_id

def get_userid_with_sessionid(session_id: str) -> int:
    if not session_id:
        return -1
    user_id = -1
    with Session(dbengine) as sss:
        query = sss.query(SessionID)\
            .filter(SessionID.session_id == session_id)
        res = query.first()
        if not res:
            return -1
        if res.expired_at <= datetime.now():
            query.delete()
            return -1
        user_id = res.user_id
    return user_id