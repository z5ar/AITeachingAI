from . import Base, sa
from enum import Enum

class ProblemType(Enum):
    single_choice = 'single_choice'
    multiple_choice = 'multiple_choice'
    variable_choice = 'variable_choice'
    blank_filling = 'blank_filling'
    brief_response = 'brief_response'

class Problem(Base):
    __tablename__ = 'problem'

    id = sa.Column(sa.Integer, primary_key=True)
    ptype = sa.Column(sa.Enum(ProblemType), nullable=False)
    problem = sa.Column(sa.Text, nullable=False)
    arms = sa.Column(sa.JSON)
    answer = sa.Column(sa.JSON)
