from . import Base, sa
from enum import Enum

class ThemeColour(Enum):
    pink = 'pink'
    orange = 'orange'
    yellow = 'yellow'
    green = 'green'
    blue = 'blue'
    purple = 'purple'

class Profile(Base):
    __tablename__ = 'profile'

    id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    nickname = sa.Column(sa.String, nullable=True)
    avatar = sa.Column(sa.String, nullable=True)
    colour = sa.Column(sa.Enum(ThemeColour), nullable=True)