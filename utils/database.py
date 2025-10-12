from . import config
import sqlalchemy as sa
import sqlalchemy.orm as sorm

Base = sorm.declarative_base()
class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(32), unique=True, nullable=False)
    nickname = sa.Column(sa.String(64), nullable=False)
    passwd_hash = sa.Column(sa.String(64), nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    deleted_at = sa.Column(sa.DateTime)

engine = sa.create_engine(url=config.database.url)
Base.metadata.create_all(engine)