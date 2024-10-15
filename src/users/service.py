import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
from typing import Optional

from fastapi import HTTPException, Request, status

from src.consts import ErrorMessages, SuccessMessages
from src.settings import logger, settings
from src.users.db_utils import create_reset_password_token


class EmailService:
    """Class for sending emails to users."""

    SENDER_EMAIL = settings.EMAIL
    _VALID_EMAIL = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,7}\b"
    )
    TO_EMAIL = None
    REQUEST = None

    @cached_property
    def __get_message(self) -> MIMEMultipart:
        """Returns the message to be sent."""

        return MIMEMultipart()

    @cached_property
    def __create_token(self) -> str:
        """Returns the token to be sent."""

        return create_reset_password_token(self.TO_EMAIL)

    @cached_property
    def __create_reset_url(self) -> str:
        """Returns the url to be sent."""

        logger.info("Creating reset url for %s" % self.TO_EMAIL)
        return self.REQUEST.url_for("reset_password", token=self.__create_token)

    def __create_reset_password_message(self) -> MIMEMultipart:
        """Create reset password email message."""

        if not self.__is_valid_email(self.TO_EMAIL):
            logger.error(
                "Error: %s, %s is not a valid email"
                % (ErrorMessages.NOT_REAL_EMAIL.value, self.TO_EMAIL)
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.NOT_REAL_EMAIL.value,
            )

        message = self.__get_message
        message["From"] = self.SENDER_EMAIL
        message["To"] = self.TO_EMAIL
        message["Subject"] = "Reset password"
        message.attach(MIMEText(str(self.__create_reset_url), "plain"))

        return message

    def __is_valid_email(self, email) -> bool:
        """Check if email is valid."""

        return bool(self._VALID_EMAIL.fullmatch(email))

    def send_email(
        self, to_email: str, message: MIMEMultipart
    ) -> Optional[dict | smtplib.SMTPException]:
        """Sends an email with a link to recover password to the given email address."""

        try:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(self.SENDER_EMAIL, settings.EMAIL_PASSWORD)
            server.sendmail(
                self.SENDER_EMAIL,
                to_email,
                message.as_string(),
            )
            server.quit()
            logger.info("Email sent to %s" % to_email)

            return {"message": SuccessMessages.SUCCESS_SENT_EMAIL.value}

        except smtplib.SMTPException as error:
            logger.error("Error: %s, User: %s" % (error, to_email))

            return {"error": str(error)}

    def send_reset_password_email(
        self, to_email: str, request: Request
    ) -> None:
        """Send reset password email."""

        self.REQUEST = request
        self.TO_EMAIL = to_email
        return self.send_email(to_email, self.__create_reset_password_message())


email_service = EmailService()
