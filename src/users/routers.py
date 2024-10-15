from typing import Dict, Any

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.consts import ErrorMessages, SuccessMessages
from src.users.auth import token_manager
from src.users.db_utils import (
    change_password,
    create_user_in_db,
    delete_reset_token_token,
    get_user_by_auth_token,
    get_user_by_reset_token,
    get_user_id_from_db,
)
from src.users.service import email_service
from src.users.shemes import BaseUser, ResetPassword, TokenData

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}/", response_model=None)
def read_users_me(
    token_data: TokenData = Depends(token_manager.verify_token),
) -> Dict[str, int | str]:
    """Read the current user."""

    return get_user_by_auth_token(token_data)


@router.post("/register/")
def register_user(user: BaseUser) -> dict:
    """Register a new user."""

    return {
        "message": SuccessMessages.SUCCESS_CREATED_USER.value,
        "email": create_user_in_db(user),
    }


@router.post("/token/", response_model=None)
def login(email: str, password: str) -> dict | HTTPException:
    """Login a user."""

    try:
        user_id = get_user_id_from_db(email, password)
        token = token_manager.create_token(user_id, email)

    except HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.INVALID_DATA.value,
        )

    return {"access_token": token}


@router.post("/request_reset_password/")
def request_reset_password(email: str, request: Request) -> dict:
    """Request a reset password email."""

    return email_service.send_reset_password_email(email, request)


@router.post("/reset_password/{token}/")
def reset_password(token: str, data: ResetPassword) -> dict:
    """Reset a password."""

    change_password(get_user_by_reset_token(token), data)
    delete_reset_token_token(token)

    return {"message": SuccessMessages.SUCCESS_RESET_PASSWORD.value}
