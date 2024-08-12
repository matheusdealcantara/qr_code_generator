import os
from io import BytesIO

import qrcode
from cs50 import SQL
from flask import Flask, render_template, request, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=['GET', 'POST'])	
def hello_world():
    if request.method == 'POST':
        data = request.form.get('url')

        if not data:
            return render_template('index.html', error='Please enter a URL')

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