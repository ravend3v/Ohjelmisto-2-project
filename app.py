from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, g, jsonify
from operations import DatabaseOperations
from password_utils import bcrypt, PasswordUtils

# Import queries
from queries import * 

from lib.crypto import *
from lib.utils import *

from api import api_bp

import geopy.distance

# Load .env.local variables
load_dotenv()

app = Flask(__name__)
bcrypt.init_app(app)

app.register_blueprint(api_bp, url_prefix='/api')

def get_access_token_middleware(func):
    def wrapper(*args, **kwargs):
        access_token_data = get_access_token(request)

        if not access_token_data['success']:
            response = app.make_response(redirect(url_for('login')))
            response.delete_cookie('session_token')
            return response, 301
        
        g.access_token_data = access_token_data
        
        return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    return wrapper

def valid_session_token_middleware(func):
    def wrapper(*args, **kwargs):
        session_token_cookie = request.cookies.get('session_token')
        decoded_session_token = valid_session_token(session_token_cookie)

        if decoded_session_token['valid']:
            return redirect('/'), 301
        
        return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    return wrapper


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'

    return r

@app.route('/', methods=['GET'])
@get_access_token_middleware
def landing_page():
    access_token_data = g.get('access_token_data')

    return render_template('landing.html', data=access_token_data), 200


@app.route('/game', methods=['GET'])
@get_access_token_middleware
def game():
    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    access_token_data = g.get('access_token_data')

    cursor.execute(GET_CURRENT_PLAYER_LOCATION_DATA, (access_token_data['user_Id'], ))
    current_airport = cursor.fetchone()
    current_airport_json = {
        'ident': current_airport[0],
        'name': current_airport[1],
        'latitude_deg': current_airport[2],
        'longitude_deg': current_airport[3],
        'continent': current_airport[4],
        'cost_of_flight': 0,
        'co2_consumtion': 0,
        'flyable': False
    }

    cursor.execute('SELECT ident, name, latitude_deg, longitude_deg, continent FROM airport')
    all_airports = cursor.fetchall()

    flyable_airports = get_flyable_airports(current_airport, all_airports)
    flyable_airports.append(current_airport_json)

    page_data = {
        'airports': flyable_airports,
        'current_airport': current_airport_json,
        'access_token_data': access_token_data,
    }

    return render_template('game.html', data=page_data)

@app.route('/sign_up', methods=['GET', 'POST'])
@valid_session_token_middleware
def sign_up():
    error_message = { 'error_message': '', 'display': 'hidden' }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = PasswordUtils.hash_password(password)
        
        conn = DatabaseOperations.get_db_connection()
        if conn is None:
            error_message['error_message'] = 'An error occured while connecting to the database.'
            error_message['display'] = 'flex'
            return render_template('sign_up.html', data=error_message)
        
        cursor = conn.cursor()

        try:
            # Check if the default location exists in the airport table
            cursor.execute("SELECT ident FROM airport WHERE ident = %s", ('',))
            if cursor.fetchone() is None:
                # Insert a valid location if the default does not exist
                cursor.execute("SELECT ident FROM airport LIMIT 1")
                valid_location = cursor.fetchone()[0]
            else:
                valid_location = ''

            cursor.execute("SELECT Id FROM player WHERE user_name = %s", (username,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO player (user_name, password, co2_consumed, money, location) VALUES (%s, %s, %s, %s, %s)",
                    (username, hashed_password, 0, 2000, valid_location))
                
                conn.commit()
                
                session_token_payload = { 'user_name': username, 'password': hashed_password, 'user_Id': cursor.lastrowid }
                response = create_session_token(session_token_payload, app)
                
                return response, 301
            else:
                error_message['error_message'] = f'User {username} already exists'
                error_message['display'] = 'flex'
                return render_template('sign-up.html', data=error_message)
        except Exception as e:
            error_message['error_message'] = e
            error_message['display'] = 'flex'
            return render_template('sign-up.html', data=error_message)
        finally:
            cursor.close()
            conn.close()
    
    response = app.make_response(render_template('sign-up.html', data=error_message))
    response.delete_cookie('session_token')
    
    return response, 200

@app.route('/login', methods=['GET', 'POST'])
@valid_session_token_middleware
def login():
    error_message = { 'error_message': '', 'display': 'hidden' }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT Id, password FROM player WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            if result and PasswordUtils.check_password(result[1], password):
                session_token_payload = { 'user_name': username, 'password': PasswordUtils.hash_password(password), 'user_Id': result[0] }
                response = create_session_token(session_token_payload, app)

                return response, 301
            else:
                error_message['error_message'] = 'Invalid username or password'
                error_message['display'] = 'flex'
                return render_template('login.html', data=error_message)
        except Exception as e:
            error_message['error_message'] = e
            error_message['display'] = 'flex'
            return render_template('login.html', data=error_message)
        finally:
            cursor.close()
            conn.close()
    
    response = app.make_response(render_template('login.html', data=error_message))
    response.delete_cookie('session_token')

    return response, 200

@app.route('/load_game', methods=['GET'])
@get_access_token_middleware
def load_game():
    access_token_data = g.get('access_token_data')
    games = get_player_games(access_token_data['user_Id'])

    page_data = {'access_token_data': access_token_data, 'games': games}
    
    return render_template('load_game.html',  data=page_data), 200

    
def get_player_games(Id):
    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(GET_GAMES, (Id, ))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
        
# Load a game by ID
@app.route('/load_game/<int:game_id>', methods=['GET'])
@get_access_token_middleware
def load_game_by_id(game_id):
    access_token_data = g.get('access_token_data')
    
    # Fetch the game data based on the game_id
    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(GET_GAME_BY_ID, (game_id,))
        game_data = cursor.fetchone()

        if not game_data:
            return jsonify({'error': True, 'message': 'Game not found'}), 404
        
        # Fetch the current player location data
        cursor.execute(GET_CURRENT_PLAYER_LOCATION_DATA, (access_token_data['user_Id'], ))
        current_airport = cursor.fetchone()
        current_airport_json = {
            'ident': current_airport[0],
            'name': current_airport[1],
            'latitude_deg': current_airport[2],
            'longitude_deg': current_airport[3],
            'continent': current_airport[4],
            'cost_of_flight': 0,
            'co2_consumtion': 0,
            'flyable': False
        }
        
        cursor.execute('SELECT ident, name, latitude_deg, longitude_deg, continent FROM airport')
        all_airports = cursor.fetchall()
        
        flyable_airports = get_flyable_airports(current_airport, all_airports)
        flyable_airports.append(current_airport_json)
        
        page_data = {
            'airports': flyable_airports,
            'current_airport': current_airport_json,
            'access_token_data': access_token_data,
        }
        
        return render_template('game.html', data=page_data)
    except Exception as e:
        return jsonify({'error': True, 'message': f'Error: {e}'}), 500
    finally:
        cursor.close()
        conn.close()
    
@app.route('/logout', methods=['GET'])
def logout():
    response = app.make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')

    return response, 301

@app.route('/start_location', methods=['GET', 'POST'])
def start_location():

    cities = [
        {"name": "Helsinki-Vantaa", "icao": "EFHK"},
        {"name": "Paris-Charles de Gaulle", "icao": "LFPO"},
        {"name": "Berlin-Tegel", "icao": "EDDB"}
    ]

    if request.method == 'POST':
        selected_location = request.form.get('location')

        if selected_location and any(city["name"] == selected_location for city in cities):
            conn = DatabaseOperations.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT ident FROM airport WHERE name = %s", (selected_location,))
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('main_game', location = selected_location), 301)
        else:
            error_message = "Please select a starting location"
            return render_template('start_location.html', error_message=error_message), 400

    return render_template('start_location.html'), 200

if __name__ == '__main__':
    app.run(debug=True)