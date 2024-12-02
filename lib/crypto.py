import os, base64, jwt

from flask import Request, Response, Flask, redirect
from operations import DatabaseOperations
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization, hashes

JWT_RSA_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
JWT_RSA_PUBLIC_KEY = JWT_RSA_PRIVATE_KEY.public_key()

SESSION_TOKEN_ALGO = 'RS256'
ACCESS_TOKEN_ALGO = 'HS256'

def generate_secure_radnom_string(length: int) -> str:
    random_bytes = os.urandom(length)

    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')[:length]

def valid_session_token(token: str):
    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    try:
        decoded_session_token = jwt.decode(token, JWT_RSA_PUBLIC_KEY, algorithms=SESSION_TOKEN_ALGO)
        user = decoded_session_token['user_name']

        cursor.execute("SELECT Id FROM player WHERE user_name = %s", (user,))
        if cursor.fetchone() is None:
            return { 'valid': False, 'user': '', 'user_Id': '' }
        return { 'valid': True, 'user': user, 'user_Id': decoded_session_token['user_Id'] }
    except:
        return { 'valid': False, 'user': '', 'user_Id': '' }
    finally:
        conn.close()
        cursor.close()

def valid_access_token(access_token: str, session_token: str):
    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    try:
        decoded_session_token = valid_session_token(session_token)
        if not decoded_session_token['valid']:
            return { 'valid': False, 'message': 'Invalid session token' }
        
        decoded_access_token = jwt.decode(access_token, session_token, algorithms=ACCESS_TOKEN_ALGO)
        if decoded_access_token['user_name'] == decoded_session_token['user']:
            return { 'valid': True, 'message': 'Valid tokens' }
        return { 'valid': False, 'message': 'Invalid access token' }
    
    except Exception as e:
        return { 'valid': False, 'message': f'{e}' }
    
    finally:
        conn.close()
        cursor.close()


def create_session_token(payload, app: Flask) -> Response:
    session_token = jwt.encode(payload, JWT_RSA_PRIVATE_KEY, algorithm=SESSION_TOKEN_ALGO)

    response = app.make_response(redirect('/'))
    response.set_cookie('session_token', session_token,
                        expires=datetime.now() + timedelta(days=7),
                        httponly=True,
                        samesite='Strict')
    
    return response


def get_access_token(req: Request):
    session_token = req.cookies.get('session_token')
    response_body = { 'success': False, 'access_token': '', 'user': '', 'user_Id': '' }

    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    if session_token:
        print("this happens")
        try:
            decoded_session_token = valid_session_token(session_token)
            if not decoded_session_token['valid']:
                print(decoded_session_token)
                return response_body
            
            print(decoded_session_token)
            
            access_token_payload = { 
                'user_name': decoded_session_token['user'], 
                'user_Id': decoded_session_token['user_Id'],
                'ttl': str(datetime.now() + timedelta(hours=1)), 
                'salt': generate_secure_radnom_string(16)
                }
            access_token = jwt.encode(access_token_payload, session_token, algorithm=ACCESS_TOKEN_ALGO)
            print(access_token)

            response_body['success'] = True
            response_body['access_token'] = access_token
            response_body['user'] = decoded_session_token['user']
            response_body['user_Id'] = decoded_session_token['user_Id']

            return response_body
        
        except Exception as e:
            print(e)
            return response_body
        
        finally:
            conn.close()
            cursor.close()

    # return response_body

