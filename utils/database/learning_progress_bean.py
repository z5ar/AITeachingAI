from . import Base, sa
from datetime import datetime

'''
CREATE TABLE learning_progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    section_id INT NOT NULL,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00, -- 0.00 到 100.00
    time_spent_minutes INT DEFAULT 0, -- 已学习时长
    is_completed BOOLEAN DEFAULT FALSE,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES course_sections(section_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_section (user_id, section_id),
    INDEX idx_user_course (user_id, course_id),
    INDEX idx_last_accessed (last_accessed)
);
'''
class LearningProgress(Base):
    __tablename__ = 'learning_progress'

    id = sa.Column(sa.Integer, primary_key=True)
    section_id = sa.Column(sa.Integer, sa.ForeignKey('course_section.id', ondelete='CASCADE'), nullable=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    percentage = sa.Column(sa.DECIMAL(5, 2), nullable=True, default=0)
    time_spent = sa.Column(sa.Integer, default=0)
    started_at = sa.Column(sa.DateTime, default=datetime.now)
    completed_at = sa.Column(sa.DateTime)

    __table_args__ = (
        sa.Index('prg_idx', 'user_id', 'section_id'),
    )