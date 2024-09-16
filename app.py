from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from models.conn import db
from models.model import *

from routes.auth import auth as bp_auth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_hello_adm:Admin$00@localhost/flask_hello'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#L'opzione SQLALCHEMY_TRACK_MODIFICATIONS è una configurazione per Flask-SQLAlchemy che determina se SQLAlchemy deve o meno tenere traccia delle modifiche sugli oggetti per ogni sessione.
db.init_app(app)

app.register_blueprint(bp_auth, url_prefix='/auth')

migrate = Migrate(app, db)


# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    
    return user

# @app.route('/')
# def home2():
#     return "Hello, Flask!"

# @app.route('/<nome>')
# def home(nome):
#     return render_template("hello.html", nome=nome)

# @app.route('/value/<int:value>')
# def value(value: int):
#     return f'value: {10 + value}'

# #nome "/power" deve essere come il nome della funzione
# @app.route('/power/<int:value>')
# def power(value: int):
#     return f'value: {value * value}'

@app.route('/createuser', methods=['POST'])
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


@app.route('/testuser')
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
        
# @app.route('/createuser')
# # def create_user(username, email, password):
# def create_user():

#     username = "test"
#     email = "sus@sus.sus"
#     password = "password"
#     user = User(username=username, email=email)
#     user.set_password(password)  # Imposta la password criptata
#     db.session.add(user)  # equivalente a INSERT
#     db.session.commit()
#     return f"Utente {username} creato con successo."


if __name__ == '__main__':
    app.run(debug=True)
    
    