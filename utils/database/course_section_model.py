from . import Base, sa

class CourseSection(Base):
    __tablename__ = 'course_section'

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer, sa.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    order = sa.Column(sa.Integer, nullable=False)
    title = sa.Column(sa.String(200), nullable=False)
    content = sa.Column(sa.JSON, nullable=False)
    is_chap_title = sa.Column(sa.Boolean, default=False)
    
    __table_args__ = (
        sa.Index('sec_idx', 'course_id', 'order', unique=True),
    )