from . import Base, sa

class Course(Base):
    __tablename__ = 'course'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, nullable=False)
