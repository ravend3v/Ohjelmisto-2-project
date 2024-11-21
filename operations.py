import mysql.connector
import os
from dotenv import load_dotenv

class DatabaseOperations:
    def __init__(self):
        self.reload_db_vars()
        self.db = None
        self.cursor = None

    def reload_db_vars(self):
        for key in list(os.environ.keys()):
            if key.startswith("DB_"):
                del os.environ[key]
        load_dotenv('.env')
        print("Environment variables loaded:", os.environ)

    @staticmethod
    def get_db_connection():
        try:
            # Load .env variables
            load_dotenv()

            # Debugging statements to verify environment variables
            print(f"DB_USER: {os.environ['DB_USER']}")
            print(f"DB_PASSWORD: {os.environ['DB_PASSWORD']}")
            print(f"DB_HOST: {os.environ['DB_HOST']}")
            print(f"DB_PORT: {os.environ['DB_PORT']}")
            print(f"DB_NAME: {os.environ['DB_NAME']}")

            conn = mysql.connector.connect(
                host=os.environ['DB_HOST'],
                user=os.environ['DB_USER'],
                passwd=os.environ['DB_PASSWORD'],
                database=os.environ['DB_NAME'],
                port=os.environ['DB_PORT'],
            )

            if conn.is_connected():
                print("Database connected")
                return conn
            else:
                print("Failed to connect to the database")
                return None
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("Database connection closed")