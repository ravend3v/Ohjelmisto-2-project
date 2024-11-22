from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class PasswordUtils:
    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)