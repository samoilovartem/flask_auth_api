from datetime import datetime
from typing import Union

from core.security_setup import user_datastore
from core.settings import settings
from core.utils import ServiceException
from db.redis import redis
from db.sql import db_manager
from flask import Request, Response
from flask_jwt_extended import create_access_token, create_refresh_token
from models.models import (
    AuthHistory,
    LoginRequest,
    ModifyRequest,
    SignupRequest,
    Token,
    User,
)
from services.base import BaseService


def generate_tokens(user: User):
    """Create new access and refresh tokens for the user"""
    user_roles = [role.name for role in user.roles]

    user_data = {
        'user_id': user.id,
        'user_role': user_roles,
    }
    access_token = create_access_token(identity=user.id, additional_claims=user_data)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=user_data)
    return access_token, refresh_token


def authenticate(access_token) -> None:
    """Check that access token is fresh"""
    if not redis.get(access_token) == b'':
        raise ServiceException(
            error_code='ACCESS_TOKEN_EXPIRED', message='Access token has expired'
        )


class UserService(BaseService):
    def create_user(self, username: str, password: str, email: str):
        existing_user: User = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                error_code = self.LOGIN_EXISTS.code
                message = self.LOGIN_EXISTS.message
            else:
                error_code = self.EMAIL_EXISTS.code
                message = self.EMAIL_EXISTS.message
            raise ServiceException(error_code=error_code, message=message)

        user = user_datastore.create_user(
            username=username, password=password, email=email
        )
        db_manager.db.session.add(user)
        db_manager.db.session.commit()
        return user

    def register_user(self, username: str, password: str, email: str, user_info: dict):
        """Check that a new user with these credentials can be added,
        if so, create the user and return its access and refresh tokens"""
        user = self.create_user(username, password, email)
        access_token, refresh_token = generate_tokens(user)
        self.commit_authentication(
            user, 'signup', access_token, refresh_token, user_info
        )

        return access_token, refresh_token

    def login(self, username: str, password: str, user_info: dict) -> tuple[str, str]:
        user: User = User.query.filter(User.username == username).first()

        if not user:
            raise ServiceException(
                error_code=self.USER_NOT_FOUND.code, message=self.USER_NOT_FOUND.message
            )

        if not user.verify_password(password):
            raise ServiceException(
                error_code=self.WRONG_PASSWORD.code, message=self.WRONG_PASSWORD.message
            )

        access_token, refresh_token = generate_tokens(user)
        self.commit_authentication(
            user=user,
            event_type='login',
            access_token=access_token,
            refresh_token=refresh_token,
            user_info=user_info,
        )

        return access_token, refresh_token

    def check_user(self, user: User) -> None:
        if not user:
            raise ServiceException(
                error_code=self.USER_NOT_FOUND.code, message=self.USER_NOT_FOUND.message
            )

    def check_token(self, refresh_token: str) -> str:
        current_refresh_token = Token.query.filter(
            Token.token_value == refresh_token
        ).first()
        if not current_refresh_token:
            raise ServiceException(
                error_code=self.INVALID_REFRESH_TOKEN.code,
                message=self.INVALID_REFRESH_TOKEN.message,
            )
        return current_refresh_token

    def refresh(self, user_id: str, refresh_token: str) -> tuple[str, str]:
        user: User = User.query.get(user_id)

        self.check_user(user)
        current_refresh_token = self.check_token(refresh_token)

        access_token, refresh_token = generate_tokens(user)
        db_manager.db.session.delete(current_refresh_token)
        db_manager.db.session.commit()

        self.commit_authentication(
            user=user,
            event_type='refresh',
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return access_token, refresh_token

    def logout(self, user_id: str, access_token: str, refresh_token: str):
        user: User = User.query.get(user_id)

        authenticate(access_token)

        self.check_user(user)
        current_refresh_token = self.check_token(refresh_token)

        # Delete the access token
        db_manager.db.session.delete(current_refresh_token)
        db_manager.db.session.commit()

        # Delete the refresh token
        redis.delete(access_token)

        return access_token, refresh_token

    def get_auth_history(self, user_id):
        history: list[AuthHistory] = AuthHistory.query.filter(
            (AuthHistory.user_id == user_id)
        ).all()

        result = []
        for event in history:
            result.append(
                {
                    'uuid': event.id,
                    'time': event.auth_event_time,
                    'fingerprint': event.auth_event_fingerprint,
                }
            )
        return result

    def modify(self, user_id, new_username: str, new_password: str):
        user: User = User.query.get(user_id)

        if not user:
            raise ServiceException(error_code=self.USER_NOT_FOUND.code,
                                   message=self.USER_NOT_FOUND.message)

        if not new_username == user.username:
            existing_user = User.query.filter(
                (User.username == new_username)
            ).first()

            if existing_user:
                raise ServiceException(error_code=self.LOGIN_EXISTS.code,
                                       message=self.LOGIN_EXISTS.message)

            user.user_login = new_username

        if not new_password == user.password:
            user.password = new_password

        if db_manager.db.session.is_modified(user):
            db_manager.db.session.commit()

    @staticmethod
    def commit_authentication(
        user: User,
        event_type: str,
        access_token: str,
        refresh_token: str,
        user_info: dict = None,
    ):
        """Finalize successful authentication saving the details."""
        # TODO: Delete expires_at placeholder
        token = Token(
            token_owner_id=user.id, token_value=refresh_token, expires_at=datetime.now()
        )
        db_manager.db.session.add(token)

        if event_type == 'login':
            auth_event = AuthHistory(
                user_id=user.id,
                ip_address='127.0.0.1',  # TODO: получить айпи пользователя
                user_agent='Mozilla/5.0 (<system-information>) <platform> (<platform-details>) <extensions>',
                auth_event_type=event_type,
                auth_event_fingerprint=str(user_info),
            )
            db_manager.db.session.add(auth_event)

        db_manager.db.session.commit()
        redis.set(name=access_token, value='', ex=settings.jwt_access)

    def validate_signup(self, request: Request) -> Union[SignupRequest, Response]:
        return self._validate(request, SignupRequest)

    def validate_login(self, request: Request) -> Union[LoginRequest, Response]:
        return self._validate(request, LoginRequest)

    def validate_modify(self, request: Request) -> Union[ModifyRequest, Response]:
        return self._validate(request, ModifyRequest)
