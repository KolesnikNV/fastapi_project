from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Users(Base):
    """Users table in DB."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    password_reset_token = relationship("PasswordResetToken")


class PasswordResetToken(Base):
    """Password reset token table in DB."""

    __tablename__ = "password_reset_token"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("Users", back_populates="password_reset_token")
