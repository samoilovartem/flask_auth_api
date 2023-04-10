from api.v1.roles.routes import role
from api.v1.social.routes import social
from api.v1.user.routes import user
from flask import Blueprint, jsonify

v1 = Blueprint('v1', __name__, url_prefix='/v1')
v1.register_blueprint(user)
v1.register_blueprint(social)
v1.register_blueprint(role)


@v1.route('/')
def index():
    return jsonify(result='Hello, World!')
