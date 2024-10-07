from flask import Blueprint, request, render_template
from flask_login import login_user, logout_user, login_required
from models.conn import db
from models.model import *

old = Blueprint('old', __name__)

@old.route('/createuser', methods=['POST'])
def create_user():
    values = request.json
    username = values['username']
    email = values['email']
    password = values['password']
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return f"utente {username} creato con successo."


@old.route('/testuser')
def test_user():
    # Creazione di un nuovo utente con una password criptata
    user = User(username='testuser', email='test@example.com')
    user.set_password('mysecretpassword')

    # Aggiunta dell'utente al database
    db.session.add(user)
    db.session.commit()

    # Verifica della password
    if user.check_password('mysecretpassword'):
        return "Password corretta!"
    else:
        return "Password errata!"
        
@old.route('/dashboard')
@login_required
@user_has_role('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')    

