import os
from dotenv import load_dotenv
import mariadb
from flask import Flask, request, render_template, redirect, url_for
from operations import DatabaseOperations
from password_utils import bcrypt, PasswordUtils

# Load .env.local variables
load_dotenv("'.env'")
print("Environment variables loaded:", os.environ)

app = Flask(__name__)
bcrypt.init_app(app)

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password
        hashed_password = PasswordUtils.hash_password(password)
        
        # Debugging statements
        print(f"Username: {username}")
        print(f"Hashed Password: {hashed_password}")
        
        conn = DatabaseOperations.get_db_connection()
        if conn is None:
          return "An error occured while connecting to the database."
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO player (user_name, password, co2_consumed, money, location) VALUES (?, ?, ?, ?, ?)", 
                          (username, hashed_password, 0, 0, ''))
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
            cursor.execute("SELECT password FROM player WHERE user_name = ?", (username,))
            result = cursor.fetchone()
            if result and PasswordUtils.check_password(result[0], password):
                return "Login successful"
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