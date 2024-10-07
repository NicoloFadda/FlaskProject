from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.conn import db
from models.model import *
from captcha.image import ImageCaptcha
from flask import send_file
from io import BytesIO
import random
import string


auth = Blueprint('auth', __name__)

captcha_type = 'text'

# Funzione per generare un testo CAPTCHA casuale
def generate_captcha_text(length=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Route per generare un nuovo CAPTCHA
@auth.route('/captcha_image')
def captcha_image():
    captcha_text = generate_captcha_text()
    session['captcha_solution'] = captcha_text  # Salva la soluzione del CAPTCHA nella sessione
    image = ImageCaptcha(width=300, height=100)
    image_data = BytesIO()
    image.generate(captcha_text)
    image.write(captcha_text, image_data)
    image_data.seek(0)
    return send_file(image_data, mimetype='image/png')


def generate_image_captcha():
    image = ImageCaptcha(width=200, height=100)
    text = generate_captcha_text(6)
    image_data = BytesIO()
    image.generate(text)
    image.write(text, image_data)
    return text, image_data


def generate_math_captcha():
    a, b = random.randint(1, 10), random.randint(1, 10)
    op = random.choice(['+', '-', '*'])
    if op == '+':
        solution = a + b
    elif op == '-':
        solution = a - b
    elif op == '*':
        solution = a * b
    expression = f"{a} {op} {b}"
    return expression, solution


@auth.route('/new_captcha')
def new_captcha():
    global captcha_solution, captcha_type
    
    if captcha_type == 'text':
        captcha_solution = generate_captcha_text()
        image = ImageCaptcha(width=300, height=100)
        data = image.generate(captcha_solution)
        image_data = BytesIO(data.read())
    elif captcha_type == 'math':
        captcha_solution, image = generate_math_captcha()
        image = ImageCaptcha(width=300, height=100)
        data = image.generate(captcha_solution)
        image_data = BytesIO(data.read())
    elif captcha_type == 'image':
        captcha_solution, image_data = generate_image_captcha()
    
    image_data.seek(0)
    return send_file(image_data, mimetype='image/png')


# Route per verificare il CAPTCHA
def verify_captcha(input_text):
    global captcha_solution
    return input_text == captcha_solution


#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------

# API per ottenere informazioni sul CAPTCHA
@auth.route('/api/captcha', methods=['GET'])
def api_captcha():
    global captcha_solution, captcha_type
    response = {
        'type': captcha_type,
        'solution': captcha_solution
    }
    return jsonify(response)

#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------

@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
#-------------------------------------------------------------------------------------------------------------------------
    captcha_input = request.form.get('captcha_input')  # Input CAPTCHA dal form

    # Verifica del CAPTCHA
    if not verify_captcha(captcha_input):
        flash('CAPTCHA non valido. Riprova.')
        return redirect(url_for('auth.login'))
#-------------------------------------------------------------------------------------------------------------------------
    stmt = db.select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalar_one_or_none()
#-------------------------------------------------------------------------------------------------------------------------
    if not user or not user.check_password(password):
        flash('Controlla i tuoi dati di accesso e riprova.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))
#-------------------------------------------------------------------------------------------------------------------------
@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
#-------------------------------------------------------------------------------------------------------------------------
    captcha_input = request.form.get('captcha_input')  # Input CAPTCHA dal form

    # Verifica del CAPTCHA
    if not verify_captcha(captcha_input):
        flash('CAPTCHA non valido. Riprova.')
        return redirect(url_for('auth.signup'))

    if not username or not email or not password:
        flash('Compila tutti i campi.')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Esiste già un account con questo indirizzo email.')
        return redirect(url_for('auth.signup'))

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@login_required
@auth.route('/profile')
def profile():
    return render_template("/auth/profile.html", name=current_user.username)
    
@login_required
@auth.route('/logout')
def logout():
    return render_template("/auth/logout.html")