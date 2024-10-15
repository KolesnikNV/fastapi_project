from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from src.settings import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


engine = create_engine(settings.DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(
    autocommit=False,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)
