import os, base64, jwt

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
