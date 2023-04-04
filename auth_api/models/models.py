import uuid
from datetime import datetime
from enum import Enum

from flask_security import UserMixin, RoleMixin, utils
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from models.create_partitions import create_partition_auth_history, create_partition_user
from databases import db


class RoleType(str, Enum):
    user = "user"
    superuser = "superuser"


class TimeStampedMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UUIDMixin:
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


class User(UUIDMixin, TimeStampedMixin, UserMixin, db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    _password = db.Column('password', db.String(255), nullable=False)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy=True))
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


class SocialAccount(UUIDMixin, db.Model):
    __tablename__ = 'social_accounts'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    social_id = db.Column(db.String(255), nullable=False)
    social_provider_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_provider_name}:{self.user_id}>'


class AuthHistory(UUIDMixin, TimeStampedMixin, db.Model):
    __tablename__ = 'auth_history'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    is_successful = db.Column(db.Boolean, default=False, nullable=False)
    device = db.Column(db.String(255))

    def __repr__(self):
        return f'<AuthHistory {self.user_id}>'


class Role(UUIDMixin, TimeStampedMixin, RoleMixin, db.Model):
    __tablename__ = 'roles'

    name = db.Column(Enum(RoleType), db.String(50), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(UUIDMixin, db.Model):
    __tablename__ = 'user_roles'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id', ondelete='CASCADE'))


event.listen(AuthHistory.__table__, 'after_create', create_partition_auth_history)
event.listen(User.__table__, 'after_create', create_partition_user)
