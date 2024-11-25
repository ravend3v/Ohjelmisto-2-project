import os, base64, mariadb, jwt

from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, jsonify
from operations import DatabaseOperations
from password_utils import bcrypt, PasswordUtils

from lib.crypto import *

# Load .env.local variables
load_dotenv()

app = Flask(__name__)
bcrypt.init_app(app)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'

    return r

@app.route('/', methods=['GET'])
def landing_page():
    access_token_data = get_access_token(request)

    if not access_token_data['success']:
        response = app.make_response(redirect(url_for('login')))
        response.delete_cookie('session_token')
        return response, 301

    return render_template('landing.html', data=access_token_data), 200


@app.route('/game', methods=['GET'])
def game():
    return render_template('game.html')


@app.route('/sign_up', methods=['GET', 'POST'])
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
                session_token_payload = { 'user_name': username, 'password': hashed_password }
                session_token = jwt.encode(session_token_payload, JWT_RSA_PRIVATE_KEY, algorithm=SESSION_TOKEN_ALGO)

                response = app.make_response(redirect('/'))
                response.set_cookie('session_token', session_token,
                                    expires=datetime.now() + timedelta(days=7),
                                    httponly=True,
                                    samesite='Strict')
                
                cursor.execute(
                    "INSERT INTO player (user_name, password, co2_consumed, money, location) VALUES (%s, %s, %s, %s, %s)",
                    (username, hashed_password, 0, 0, valid_location))
                
                conn.commit()

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

    session_token_cookie = request.cookies.get('session_token')
    decoded_session_token = valid_session_token(session_token_cookie)

    if decoded_session_token['valid']:
        return redirect('/'), 301
    
    response = app.make_response(render_template('sign-up.html', data=error_message))
    response.delete_cookie('session_token')
    
    return response, 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = { 'error_message': '', 'display': 'hidden' }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT password FROM player WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            if result and PasswordUtils.check_password(result[0], password):
                session_token_payload = { 'user_name': username, 'password': PasswordUtils.hash_password(password) }
                session_token = jwt.encode(session_token_payload, JWT_RSA_PRIVATE_KEY, algorithm=SESSION_TOKEN_ALGO)

                response = app.make_response(redirect('/'))
                response.set_cookie('session_token', session_token,
                                    expires=datetime.now() + timedelta(days=7),
                                    httponly=True,
                                    samesite='Strict')

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

    session_token_cookie = request.cookies.get('session_token')
    decoded_session_token = valid_session_token(session_token_cookie)

    if decoded_session_token['valid']:
        return redirect('/'), 301
    
    response = app.make_response(render_template('login.html', data=error_message))
    response.delete_cookie('session_token')

    return response, 200

@app.route('/logout', methods=['GET'])
def logout():
    response = app.make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')

    return response, 301

if __name__ == '__main__':
    app.run(debug=True)