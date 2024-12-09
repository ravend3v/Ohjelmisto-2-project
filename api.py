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

        cursor.execute(UPDATE_GAME_DATA, 
                        (ident,
                        request_body_data['co2_consumption'],
                        -request_body_data['cost_of_flight'] + request_body_data['winnings'],
                        request_body_data['game_id']
                        ))
        cursor.execute(UPDATE_PLAYER_VISITED, (request_body_data['game_id'], request_body_data['continent'], request_body_data['game_id'], request_body_data['continent']))
        conn.commit()

        return jsonify({ 'error': False, 'message': 'player data updated succesfully' }), 200
    except Exception as e:
        return jsonify({ 'error': True, 'message': f'{e}' }), 500
    
    
@api_bp.route('/select_start_location', methods=['POST'])
def select_start_location():
    try:
        selected_location = request.json['location']
        user_id = request.json['user_Id']

        if not selected_location:
            return jsonify({'error': True, 'message': 'No location selected'}), 400

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        # Update the player's location

        # Create a new game
        cursor.execute(CREATE_GAME, (2000, 0, selected_location))
        game_id = cursor.lastrowid

        cursor.execute(CREATE_PLAYER_GAME, (user_id, game_id))
        conn.commit()

        return jsonify({'error': False, 'message': 'Game created successfully', 'selected_location': selected_location, 'game_id': game_id}), 200
    except Exception as e:
        return jsonify({'error': True, 'message': f'{e}'}), 500