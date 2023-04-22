from http import HTTPStatus

from flask import Blueprint, jsonify, make_response, request
from services.social import social_auth_service
from socials.interface import SocialProvider

social = Blueprint('social', __name__, url_prefix='/social')


@social.route('/', methods=['GET'])
def methods_list():
    """
    Возвращает список соц сетей для входа
    ---
    get:
      summary: Get list of social providers for auth
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
                        name:
                            type: string
                            example: Provider Name
                        request_url:
                            type: string
                            example: Provider Request url
      tags:
        - social
    """

    response = {}
    for provider in social_auth_service.iter():
        response[provider.name] = provider.request_url()

    return make_response(jsonify(response), HTTPStatus.OK)


@social.route('/handler/<provider_name>', methods=['GET'])
def handler(provider_name):
    provider: SocialProvider = social_auth_service.get_provider_by_name(provider_name)
    data = provider.get_user_info(request.args['code'])
    return jsonify(data)