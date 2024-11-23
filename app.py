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

@app.route('/', methods=['GET'])
def landing_page():
    return render_template('landing.html'), 200

@app.route('/getAccessToken', methods=['GET'])
def get_access_token():
    session_token = request.cookies.get('session_token')
    response_body = { 'redirect': True, 'access_token': '', 'user': '' }

    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    if session_token:
        try:
            decoded_session_token = jwt.decode(session_token, JWT_RSA_PUBLIC_KEY, algorithms=SESSION_TOKEN_ALGO)

            user = decoded_session_token['user_name']

            cursor.execute("SELECT Id FROM player WHERE user_name = %s", (user,))
            if cursor.fetchone() is None:
                return app.make_response(jsonify(response_body))
            
            access_token_payload = { 'user_name': user, 'ttl': str(datetime.now() + timedelta(hours=1)), 'salt': generate_secure_radnom_string(16) }
            access_token = jwt.encode(access_token_payload, session_token, algorithm=ACCESS_TOKEN_ALGO)

            response_body['redirect'] = False
            response_body['access_token'] = access_token
            response_body['user'] = user

            return app.make_response(jsonify(response_body)), 200
        
        except:
            return app.make_response(jsonify(response_body)), 500
        
        finally:
            conn.close()
            cursor.close()

    return app.make_response(jsonify(response_body)), 401


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response_body = { 'access_token': '', 'success': False, 'message': '' }
        
        # Hash the password
        hashed_password = PasswordUtils.hash_password(password)
        
        conn = DatabaseOperations.get_db_connection()
        if conn is None:
            response_body['message'] = 'An error occured while connecting to the database.'
            return app.make_response(response_body), 500
        
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

                access_token_payload = { 'user_name': username, 'ttl': str(datetime.now() + timedelta(hours=1)), 'salt': generate_secure_radnom_string(16) }
                access_token = jwt.encode(access_token_payload, session_token, algorithm=ACCESS_TOKEN_ALGO)

                response_body['access_token'] = access_token
                response_body['success'] = True

                response = app.make_response(jsonify(response_body))
                response.set_cookie('session_token', session_token,
                                    expires=datetime.now() + timedelta(days=7),
                                    httponly=True,
                                    samesite='Strict')
                
                cursor.execute(
                    "INSERT INTO player (user_name, password, co2_consumed, money, location) VALUES (%s, %s, %s, %s, %s)",
                    (username, hashed_password, 0, 0, valid_location))
                conn.commit()

                return response, 200
            else:
                response_body['message'] = f'User {username} already exists'
                return app.make_response(response_body), 400
        except Exception as e:
            response_body['message'] = e
            return app.make_response(response_body), 500
        finally:
            cursor.close()
            conn.close()

    return render_template('sign-up.html'), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = DatabaseOperations.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT password FROM player WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            if result and PasswordUtils.check_password(result[0], password):
                return "logged in!!"
            else:
                return "Invalid username or password"
        except mariadb.Error as e:
            print(f"Error: {e}")
            return "An error occurred while logging in."
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    response = app.make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')

    return response, 301

if __name__ == '__main__':
    app.run(debug=True)