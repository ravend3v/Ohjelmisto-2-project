from flask import Blueprint, request, jsonify, g
from lib.crypto import valid_access_token
from operations import DatabaseOperations
from queries import *

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def verify_access_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({ 'error': True, 'message': 'Missing Authorization header' }), 400
    
    access_token = auth_header.removeprefix('Bearer ')

    valid_token = valid_access_token(access_token, request.cookies.get('session_token'))
    if not valid_token['valid']:
        return jsonify({ 'error': True, 'message': valid_token['message'] }), 401

@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({ 'error': False, 'message': 'it works' })

@api_bp.route('/fly_to/<ident>', methods=['POST'])
def fly_to(ident):
    try:
        request_body_data = request.json

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(UPDATE_PLAYER_DATA, 
                        (ident,
                        request_body_data['co2_consumption'],
                        -request_body_data['cost_of_flight'] + request_body_data['winnings'],
                        request_body_data['user_Id']
                        ))
        cursor.execute(UPDATE_PLAYER_VISITED, (request_body_data['user_Id'], request_body_data['continent'], request_body_data['user_Id'], request_body_data['continent']))
        conn.commit()

        return jsonify({ 'error': False, 'message': 'player data updated succesfully' }), 200
    except Exception as e:
        return jsonify({ 'error': True, 'message': f'{e}' }), 500
    
    
@api_bp.route('/select_start_location', methods=['POST'])
def select_start_location():
    try:
        access_token_data = g.get('access_token_data')
        user_id = access_token_data['user_Id']
        selected_location = request.json.get('location')

        if not selected_location:
            return jsonify({'error': True, 'message': 'No location selected'}), 400

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        # Update the player's location
        cursor.execute(UPDATE_PLAYER_LOCATION, (selected_location, user_id))

        # Create a new game
        cursor.execute(CREATE_GAME, (user_id, selected_location))
        conn.commit()

        return jsonify({'error': False, 'message': 'Game created successfully', 'selected_location': selected_location}), 200
    except Exception as e:
        return jsonify({'error': True, 'message': f'{e}'}), 500