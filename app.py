import os
from io import BytesIO

import qrcode
from cs50 import SQL
from flask import Flask, redirect, render_template, request, send_file, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import apology, login_required

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///qr.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=['GET', 'POST'])
@login_required	
def hello_world():
    if request.method == 'POST':
        data = request.form.get('url')

        if not data:
            return apology('You must provide a URL', 403)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    else:
        return render_template('index.html')


@app.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.form.get('data')

    qr = qrcode.QRCode(
       version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0) 

    return send_file(img_io, mimetype='image/png')


@app.route('/history')
@login_required
def history():
    rows = db.execute('SELECT * FROM qr WHERE user_id = ?', session['user_id'])
    return render_template('history.html', rows=rows)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            return apology('You must provide a username', 403)
        
        if not password:
            return apology('You must provide a password', 403)
        
        if password != confirmation:
            return apology('Passwords do not match', 403)

        hash = generate_password_hash(password)

        try:
            db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', username, hash)
        except ValueError:
            return apology('Username already exists', 403)

        return redirect('/')
    else:
        return render_template('register.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            return apology('You must provide a username', 403)
        if not password:
            return apology('You must provide a password', 403)

        rows = db.execute('SELECT * FROM users WHERE username = ?', username)

        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], password):
            return apology('Invalid username and/or password', 403)

        session['user_id'] = rows[0]['id']

        return render_template('index.html')
    else:
        return render_template('login.html')

    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')