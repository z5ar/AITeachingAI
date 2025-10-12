from utils.config import config
import sqlalchemy as sa
import sqlalchemy.orm as sorm

Base = sorm.declarative_base()

from .user_bean import User
from .sessionid_bean import SessionID
from .course_bean import Course
from .course_section_bean import CourseSection
from .learning_progress_bean import LearningProgress

engine = sa.create_engine(url=config.database.url)
Base.metadata.create_all(engine)

__all__ = ('engine', 'User', 'SessionID', 'Course', 'CourseSection', 'LearningProgress')