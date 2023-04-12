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
    """
    Create a new role with the given name and description.
    ---
   post:
      summary: Create a new role with the given name and description.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
      - in: body
        name: requestBody
        type: object
        properties:
          name:
            type: string
          description:
            type: string
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Role created successfully
        '400':
          description: bad request
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Missing name or description
        '409':
          description: conflict
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Role already exists
        '401':
          description: unathorized
        '403':
          description: forbidden
      tags:
        - roles
    """
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
    """
    Retrieve all existing roles.
    ---
   get:
      summary: Retrieve all existing roles.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: array
                items:
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      description:
                        type: string
                      created_at:
                        type: string
                      updated_at:
                        type: string

        '401':
          description: unathorized
        '403':
          description: forbidden
      tags:
        - roles
    """
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
    """
    Update the name and/or description of the role with the given role_id.
    ---
    put:
      summary: Update the name and/or description of the role with the given role_id.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
      - in: query
        name: role_id
        type: string
      - in: body
        name: requestBody
        type: object
        properties:
          name:
            type: string
          description:
            type: string
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role updated successfully
        '401':
          description: unathorized
        '403':
          description: forbidden
        '404':
          description: Role not found
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role not found
      tags:
        - roles
    """
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
    """
    Delete the role with the given role_id.
    ---
    delete:
      summary: Delete the role with the given role_id.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
      - in: query
        name: role_id
        type: string
        required: true
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role deleted successfully
        '401':
          description: unathorized
        '403':
          description: forbidden
        '404':
          description: Role not found
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role not found
      tags:
        - roles
    """
    role = Role.query.get(role_id)

    if role is None:
        return jsonify({"error": "Role not found"}), HTTPStatus.NOT_FOUND

    db_manager.db.session.delete(role)
    db_manager.db.session.commit()

    return jsonify({"message": "Role deleted successfully"}), HTTPStatus.OK


@role.route('/assign/<user_id>', methods=['POST'])
@jwt_roles_required()
def assign_role_to_user(user_id):
    """
    Assign a role to a user by specifying the user_id and role_id in the request payload.
    ---
    post:
      summary: Assign a role to a user by specifying the user_id and role_id in the request payload.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
        required: true
      - in: query
        name: user_id
        type: string
        required: true
      - in: body
        name: requestBody
        type: object
        properties:
          role_id:
            type: string
            required: true
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role assigned to user successfully
        '401':
          description: unathorized
        '403':
          description: forbidden
        '404':
          description: Role not found
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role not found
      tags:
        - roles
    """
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
    """
    Revoke a role from a user by specifying the user_id and role_id in the request payload.
        ---
    delete:
      summary: Assign a role to a user by specifying the user_id and role_id in the request payload.
      parameters:
      - in: headers
        name: Authorization
        type: string
        example: Bearer jwt_access_token
        required: true
      - in: query
        name: user_id
        type: string
        required: true
      - in: body
        name: requestBody
        type: object
        properties:
          role_id:
            type: string
            required: true
      responses:
        '200':
          description: success
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role revoked from user successfully
        '401':
          description: unathorized
        '403':
          description: forbidden
        '404':
          description: Role not found
          content:
            application/json:
              schema:
                type: object
                properties:
                    message:
                        type: string
                        example: Role not found
        '409':
          description: conflict
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: User does not have this role"
      tags:
        - roles
    """
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
