import os, base64, jwt

from flask import Request
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
            return { 'valid': False, 'user': '' }
        return { 'valid': True, 'user': user }
    except:
        return { 'valid': False, 'user': '' }
    finally:
        conn.close()
        cursor.close()


def get_access_token(req: Request):
    session_token = req.cookies.get('session_token')
    response_body = { 'success': False, 'access_token': '', 'user': '' }

    conn = DatabaseOperations.get_db_connection()
    cursor = conn.cursor()

    if session_token:
        try:
            decoded_session_token = valid_session_token(session_token)
            if not decoded_session_token['valid']:
                return response_body
            
            access_token_payload = { 
                'user_name': decoded_session_token['user'], 
                'ttl': str(datetime.now() + timedelta(hours=1)), 
                'salt': generate_secure_radnom_string(16)
                }
            access_token = jwt.encode(access_token_payload, session_token, algorithm=ACCESS_TOKEN_ALGO)

            response_body['success'] = True
            response_body['access_token'] = access_token
            response_body['user'] = decoded_session_token['user']

            return response_body
        
        except:
            return response_body
        
        finally:
            conn.close()
            cursor.close()

    return response_body

