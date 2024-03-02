from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Database configuration
host= 'localhost'
user='root'
password='root'
database='sign_up_login'

# Database configuration
db = mysql.connector.connect(
    host = host,
    user = user,
    password = password,
    database= database
)
cursor = db.cursor()

# Create users table if not exists
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insert user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user credentials
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            return render_template('signup.html', username=username)
        else:
            return "Login failed. Invalid credentials."

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
