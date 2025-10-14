from utils.config import config
import sqlalchemy as sa
import sqlalchemy.orm as sorm
from sqlalchemy.orm import Session

Base = sorm.declarative_base()

from .user_model import User
from .sessionid_model import SessionID
from .course_model import Course
from .course_section_model import CourseSection
from .learning_progress_model import LearningProgress
from .problem_model import Problem

engine = sa.create_engine(url=config.database.url)
Base.metadata.create_all(engine)

__all__ = ('engine', 'User', 'SessionID', 'Course', 'CourseSection', 'LearningProgress', 'Problem')