from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=5,            # keep up to 5 connections open and ready
    max_overflow=10,        # allow up to 10 extra temporary connections under load
    pool_pre_ping=True,     # test a connection before using it, so stale ones are replaced
)

SessionLocal = sessionmaker(
    bind=engine,            # sessions use this engine
    autoflush=False,        # do not send pending changes automatically before queries
    expire_on_commit=False, # keep object values readable after commit
)


class Base(DeclarativeBase):   # every model class inherits from this
    pass