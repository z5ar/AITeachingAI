from . import Base, sa
from enum import Enum

class SectionType(Enum):
    video = 'video'
    text = 'text'
    assignment = 'assignment'
    title = 'title'

class CourseSection(Base):
    
    __tablename__ = 'course_section'

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer, sa.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    order = sa.Column(sa.Integer, nullable=False)
    title = sa.Column(sa.String(200), nullable=False)
    content_type = sa.Column(sa.Enum(SectionType), nullable=False)

    __table_args__ = (
        sa.Index('sec_idx', 'course_id', 'order'),
    )

    