from http import HTTPStatus

from core.security_setup import user_datastore
from core.utils import jwt_roles_required
from db.sql import db_manager
from flask import Blueprint, jsonify, make_response, request
from models.models import Role, User, UserRole

role = Blueprint('role', __name__, url_prefix='/role')


@role.route('/', methods=['POST'])
@jwt_roles_required()
def create_role():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({"error": "Missing name or description"}), HTTPStatus.BAD_REQUEST

    if user_datastore.find_role(name):
        return jsonify({"error": "Role already exists"}), HTTPStatus.CONFLICT

    user_datastore.create_role(name=name, description=description)
    db_manager.db.session.commit()

    return make_response(
        jsonify({"message": "Role created successfully"}), HTTPStatus.CREATED
    )


@role.route('/', methods=['GET'])
@jwt_roles_required()
def view_roles():
    roles = Role.query.all()
    result = []

    for role in roles:
        role_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
        }
        result.append(role_data)

    return jsonify({"roles": result}), HTTPStatus.OK


@role.route('/<role_id>', methods=['PUT'])
@jwt_roles_required()
def update_role(role_id):
    role = Role.query.get(role_id)

    if role is None:
        return jsonify({"error": "Role not found"}), HTTPStatus.NOT_FOUND

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if name:
        role.name = name

    if description:
        role.description = description

    db_manager.db.session.commit()

    return jsonify({"message": "Role updated successfully"}), HTTPStatus.OK


@role.route('/<role_id>', methods=['DELETE'])
@jwt_roles_required()
def delete_role(role_id):
    role = Role.query.get(role_id)

    if role is None:
        return jsonify({"error": "Role not found"}), HTTPStatus.NOT_FOUND

    db_manager.db.session.delete(role)
    db_manager.db.session.commit()

    return jsonify({"message": "Role deleted successfully"}), HTTPStatus.OK


@role.route('/assign/<user_id>', methods=['POST'])
@jwt_roles_required()
def assign_role_to_user(user_id):
    data = request.json

    if not data or 'role_id' not in data:
        return (
            jsonify({"error": "Missing role_id in request payload"}),
            HTTPStatus.BAD_REQUEST,
        )

    role_id = data['role_id']
    role = Role.query.get(role_id)
    user = User.query.get(user_id)

    if role is None or user is None:
        return jsonify({"error": "Role or user not found"}), HTTPStatus.NOT_FOUND

    user_role = UserRole.query.filter_by(user_id=user.id, role_id=role.id).first()
    if user_role is not None:
        return jsonify({"error": "User already has this role"}), HTTPStatus.CONFLICT

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_manager.db.session.add(user_role)
    db_manager.db.session.commit()

    return jsonify({"message": "Role assigned to user successfully"}), HTTPStatus.OK


@role.route('/revoke/<user_id>', methods=['DELETE'])
@jwt_roles_required()
def revoke_role_from_user(user_id):
    data = request.json

    if not data or 'role_id' not in data:
        return (
            jsonify({"error": "Missing role_id in request payload"}),
            HTTPStatus.BAD_REQUEST,
        )

    role_id = data['role_id']
    role = Role.query.get(role_id)
    user = User.query.get(user_id)

    if role is None or user is None:
        return jsonify({"error": "Role or user not found"}), HTTPStatus.NOT_FOUND

    user_role = UserRole.query.filter_by(user_id=user.id, role_id=role.id).first()
    if user_role is None:
        return jsonify({"error": "User does not have this role"}), HTTPStatus.CONFLICT

    db_manager.db.session.delete(user_role)
    db_manager.db.session.commit()

    return jsonify({"message": "Role revoked from user successfully"}), HTTPStatus.OK
