from . import Base, sa

class SessionID(Base):
    __tablename__ = 'sessionid'

    id = sa.Column(sa.Integer, primary_key=True)
    session_id = sa.Column(sa.String(32), unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'))
    expired_at = sa.Column(sa.DateTime)