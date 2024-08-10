from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import boto3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

S3_BUCKET = 'nomad-tictactoe-project'
S3_REGION = 'us-east-1'
s3_client = boto3.client('s3', region_name=S3_REGION)

# In-memory user storage (for demonstration purposes; replace with a database in production)
users = {}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please log in.')
            return redirect(url_for('login'))
        users[username] = generate_password_hash(password)
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            flash('User not found. Please register first.')
            return redirect(url_for('register'))
        user_password_hash = users.get(username)
        if check_password_hash(user_password_hash, password):
            session['username'] = username
            return redirect(url_for('game'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/game')
def game():
    if 'username' not in session:
        flash('Please log in to access the game.')
        return redirect(url_for('login'))
    return render_template('game.html')

@app.route('/download')
def download():
    if 'username' not in session:
        flash('Please log in to access the download.')
        return redirect(url_for('login'))

    file_name = 'flappybird-executable.zip'
    file_path = os.path.join('/tmp', file_name)
    s3_client.download_file(S3_BUCKET, file_name, file_path)
    return send_from_directory('/tmp', file_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
