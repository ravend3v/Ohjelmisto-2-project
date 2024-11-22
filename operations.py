import mysql.connector
import os
from dotenv import load_dotenv, find_dotenv

#find the .env file and see if it exists
env_file = find_dotenv(f'.env')

class DatabaseOperations:
    def __init__(self):
        self.reload_db_vars()
        self.db = None
        self.cursor = None

    def reload_db_vars(self):
        for key in list(os.environ.keys()):
            if key.startswith("DB_"):
                del os.environ[key]
        load_dotenv(env_file)

    @staticmethod
    def create_connection():
        return mysql.connector.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            passwd=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME'],
            port=os.environ['DB_PORT'],
            collation=os.environ['DB_COLLATION']
        )

    @staticmethod
    def get_db_connection():
        try:
            # Load .env variables
            load_dotenv(env_file)

            conn = DatabaseOperations.create_connection()

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