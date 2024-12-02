from flask import Blueprint, request, jsonify
from lib.crypto import valid_access_token

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def verify_access_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({ 'error': True, 'message': 'Missing Authorization header' })
    
    access_token = auth_header.removeprefix('Bearer ')

    valid_token = valid_access_token(access_token, request.cookies.get('session_token'))
    if not valid_token['valid']:
        return jsonify({ 'error': True, 'message': valid_token['message'] })


@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({ 'error': False, 'message': 'it works' })