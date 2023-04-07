import uuid

from datetime import datetime
from enum import Enum

from core.settings import settings
from db.sql import db_manager
from flask_security import RoleMixin, UserMixin, utils
from models.create_partitions import (
    create_partition_auth_history,
    create_partition_user,
)
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import FetchedValue, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

db = db_manager.db


class RoleType(str, Enum):
    __table_args__ = {'schema': settings.postgres_schema}
    user = 'user'
    superuser = 'superuser'


class TimeStampedMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UUIDMixin:
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class User(UUIDMixin, TimeStampedMixin, UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': settings.postgres_schema}
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column('password', db.String(255), nullable=False)
    roles = db.relationship(
        'Role', secondary='user_roles', backref=db.backref('users', lazy=True)
    )
    is_totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(255))
    social_accounts = db.relationship('SocialAccount', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext_password):
        self._password = utils.hash_password(plaintext_password)

    def verify_password(self, plaintext_password):
        return utils.verify_password(plaintext_password, self._password)


class LoginRequest(BaseModel):
    username: constr(min_length=1, strip_whitespace=True, to_lower=True)
    password: constr(min_length=1, strip_whitespace=True)


class SignupRequest(LoginRequest):
    email: EmailStr


class ModifyRequest(LoginRequest):
    pass


class UserRoleAssignRequest(BaseModel):
    role_uuid: str


class SocialAccount(UUIDMixin, db.Model):
    __tablename__ = 'social_accounts'
    __table_args__ = {'schema': settings.postgres_schema}
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    social_id = db.Column(db.String(255), nullable=False)
    social_provider_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_provider_name}:{self.user_id}>'


class AuthHistory(UUIDMixin, TimeStampedMixin, db.Model):
    __tablename__ = 'auth_history'
    __table_args__ = {'schema': settings.postgres_schema}
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    is_successful = db.Column(db.Boolean, default=False, nullable=False)
    device = db.Column(db.String(255))
    auth_event_type = db.Column(db.String, nullable=False)
    auth_event_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    auth_event_fingerprint = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<AuthHistory {self.user_id}>'


class Role(UUIDMixin, TimeStampedMixin, RoleMixin, db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'schema': settings.postgres_schema}
    name = db.Column(db.Enum(RoleType), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(UUIDMixin, db.Model):
    __tablename__ = 'user_roles'
    __table_args__ = {'schema': settings.postgres_schema}
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    role_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey('roles.id', ondelete='CASCADE')
    )


event.listen(AuthHistory.__table__, 'after_create', create_partition_auth_history)
event.listen(User.__table__, 'after_create', create_partition_user)


class Token(UUIDMixin, db.Model):
    __tablename__ = 'tokens'
    __table_args__ = {'schema': settings.postgres_schema}
    token_owner_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(f'{settings.postgres_schema}.users.id'),
        nullable=False,
    )
    token_value = db.Column(db.String, nullable=False)
    token_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    expires_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=FetchedValue()
    )

    def __repr__(self):
        return f'<Token {self.token_owner_id, self.token_value}>'
