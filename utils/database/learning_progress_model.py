from . import Base, sa
from datetime import datetime

class LearningProgress(Base):
    __tablename__ = 'learning_progress'

    id = sa.Column(sa.Integer, primary_key=True)
    section_id = sa.Column(sa.Integer, sa.ForeignKey('course_section.id', ondelete='CASCADE'), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    percentage = sa.Column(sa.DECIMAL(5, 2), default=0)
    time_spent = sa.Column(sa.Integer, default=0)
    started_at = sa.Column(sa.DateTime, default=datetime.now)
    completed_at = sa.Column(sa.DateTime)
    draft = sa.Column(sa.JSON)

    __table_args__ = (
        sa.Index('prg_idx', 'user_id', 'section_id', unique=True),
    )