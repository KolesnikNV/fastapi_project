import secrets
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy import select

from src.database import SessionLocal
from src.consts import ErrorMessages
from src.settings import logger
from src.users.auth import token_manager
from src.users.models import PasswordResetToken, Users
from src.users.shemes import BaseUser, ResetPassword, TokenData


def hash_password(password: str) -> str:
    """Hash password."""

    return token_manager.pwd_context.hash(password)


def create_user_in_db(user: BaseUser) -> str:
    """Create user in database."""

    with SessionLocal() as session:
        if session.execute(select(Users).filter_by(email=user.email)).first():
            logger.error("User: %s already registered!" % user.username)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.USER_ALREADY_REGISTERED.value,
            )

        new_user = Users(
            email=user.email,
            username=user.username,
            last_name=user.last_name,
            first_name=user.first_name,
            password=hash_password(user.password),
        )

        logger.info("User with email - %s created" % user.email)

        session.add(new_user)
        session.commit()

        return new_user.email


def change_password(user: Users, data: ResetPassword) -> None:
    """Change password."""

    with SessionLocal() as session:

        if data.password != data.confirm_password:
            logger.error(
                "Email: %s | password: %s | confirm_password: %s | %s"
                % (
                    user.email,
                    data.password,
                    data.confirm_password,
                    ErrorMessages.PASSWORDS_DO_NOT_MATCH.value,
                )
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.PASSWORDS_DO_NOT_MATCH.value,
            )

        user.password = hash_password(data.password)

        session.add(user)
        session.commit()

        logger.info("User with email - %s changed password" % user.email)


def get_user_id_from_db(email: str, password: str) -> None | Users:
    """Get user from db."""

    with SessionLocal() as session:
        user = session.execute(
            select(Users).where(Users.email == email)
        ).scalar_one_or_none()

        if user is None or not token_manager.verify_password(
            password, user.password
        ):
            logger.error(
                "Email: %s | %s | %s"
                % (
                    email,
                    ErrorMessages.INVALID_EMAIL.value,
                    ErrorMessages.PASSWORDS_DO_NOT_MATCH,
                )
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{ErrorMessages.INVALID_EMAIL.value} or {ErrorMessages.PASSWORDS_DO_NOT_MATCH}",
            )

        return user.id


def get_user_by_auth_token(token_data: TokenData) -> Dict[str, str]:
    """Get user by auth token."""

    with SessionLocal() as session:
        user = session.execute(
            select(Users).filter_by(
                id=token_data.user_id, email=token_data.email
            )
        ).scalar_one_or_none()

        if user is None:
            logger.error("Error: %s" % ErrorMessages.INVALID_TOKEN.value)

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_dict = user.__dict__
        user_dict.pop("password", None)

        return user_dict


def get_user_by_reset_token(token: str) -> Users:
    """Get user by reset token."""

    with SessionLocal() as session:
        token = session.execute(
            select(PasswordResetToken).filter_by(token=token)
        ).scalar_one_or_none()

        if token is None:
            logger.error("Error: %s" % ErrorMessages.INVALID_TOKEN.value, token)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_TOKEN.value,
            )

        return token.user


def create_reset_password_token(email: str) -> str:
    """Create reset password token."""

    LEN_BYTES = 32

    with SessionLocal() as session:
        user = session.execute(
            select(Users).filter_by(email=email)
        ).scalar_one_or_none()

        if user is None:
            logger.error("Email: %s not found!" % email)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.INVALID_EMAIL.value,
            )

        random_token = secrets.token_urlsafe(LEN_BYTES)
        session.add(PasswordResetToken(token=random_token, user=user))
        session.commit()

        return random_token


def delete_reset_token_token(token: str) -> None:
    """Delete reset token."""

    with SessionLocal() as session:
        token = session.execute(
            select(PasswordResetToken).filter_by(token=token)
        ).scalar_one_or_none()

        session.delete(token)
        session.commit()

        logger.info("Reset password token %s deleted" % token)
