from http import HTTPStatus

from flask import Blueprint, make_response, request, jsonify

from services.social import social_auth_service
from socials.interface import SocialProvider

social = Blueprint('social', __name__, url_prefix='/social')


@social.route('/', methods=["GET"])
def methods_list():
    provider: SocialProvider = social_auth_service.get_provider_by_name("google")
    handler_path: str = f"{request.base_url}handler/"
    response_template = f"""
        <a href='{provider.redirect_url(handler_path)}'>{provider.name}</a>
    """
    return make_response(
        response_template, HTTPStatus.OK
    )


@social.route('/handler/<provider_name>', methods=["GET"])
def handler(provider_name):
    provider: SocialProvider = social_auth_service.get_provider_by_name(provider_name)
    data = provider.get_user_info(request.args["code"])
    return jsonify(data)
