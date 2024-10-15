from functools import cached_property
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.consts import ErrorMessages
from src.settings import logger, settings
from src.users.shemes import TokenData


class TokenManager:
    """Class for managing tokens."""

    _SECRET_KEY = settings.SECRET_KEY
    _ALGORITHM = settings.ALGORITHM

    def __init__(self):
        self.__token = None

    @cached_property
    def return_error(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.BAD_CREDENTIALS.value,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @cached_property
    def _get_pwd_context(self) -> CryptContext:
        """Returns password context."""

        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    @cached_property
    def _get_email(self) -> str | None:
        """Returns email."""

        return self._decode_token(self.__token).get("email")

    @cached_property
    def _get_user_id(self) -> int | None:
        """Returns user id."""

        return self._decode_token(self.__token).get("user_id")

    @cached_property
    def _get_data_from_token(self) -> TokenData:
        """Gets data from token."""

        email: str = self._get_email
        user_id: int = self._get_user_id

        return TokenData(email=email, user_id=user_id)

    def _decode_token(self, token) -> Dict[str, Any]:
        """Decodes a JWT token."""

        return jwt.decode(token, self._SECRET_KEY, algorithms=[self._ALGORITHM])

    def create_token(self, email: str, user_id: int) -> str:
        """Creates a JWT token."""

        data = {"email": email, "user_id": user_id}

        return jwt.encode(data, self._SECRET_KEY, algorithm=self._ALGORITHM)

    def verify_token(
        self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))
    ) -> TokenData:
        """Verifies a token."""

        self.__token = token
        try:
            return self._get_data_from_token

        except JWTError as exc:
            logger.error(
                "Error: %s | %s" % (ErrorMessages.BAD_CREDENTIALS.value, exc)
            )

            raise self.return_error

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verifies a password."""

        return self._get_pwd_context.verify(plain_password, hashed_password)


token_manager = TokenManager()
