from pydantic import BaseModel


class TokenData(BaseModel):
    """Token data to be used in the JWT auth."""

    user_id: int
    email: str


class BaseUser(BaseModel):
    """Base user model."""

    username: str
    email: str
    first_name: str = None
    last_name: str = None
    password: str


class ResetPassword(BaseModel):
    """Reset password model."""

    password: str
    confirm_password: str
