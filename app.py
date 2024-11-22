import os
from dotenv import load_dotenv
import mariadb
from flask import Flask, request, render_template, redirect, url_for
from operations import DatabaseOperations
from password_utils import bcrypt, PasswordUtils

# Load .env.local variables
load_dotenv()

app = Flask(__name__)
bcrypt.init_app(app)

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password
        hashed_password = PasswordUtils.hash_password(password)
        
        conn = DatabaseOperations.get_db_connection()
        if conn is None:
            return "An error occured while connecting to the database."
        
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

            cursor.execute(
                "INSERT INTO player (user_name, password, co2_consumed, money, location) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_password, 0, 0, valid_location))
            conn.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
            return "An error occurred while signing up."
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('login'))

    return render_template('sign-up.html')

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
                return render_template('landing.html')
            else:
                return "Invalid username or password"
        except mariadb.Error as e:
            print(f"Error: {e}")
            return "An error occurred while logging in."

        cursor.close()
        conn.close()

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)