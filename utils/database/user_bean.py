from . import Base, sa

class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(32), nullable=False)
    passwd_hash = sa.Column(sa.String(64), nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    logged_in_at = sa.Column(sa.DateTime)
    deleted_at = sa.Column(sa.DateTime)