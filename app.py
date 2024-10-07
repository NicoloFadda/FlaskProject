from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user
# from dotenv import load_dotenv
import os
from flask import Flask
from flask_admin import Admin   # nuovo
import sys  # Necessario per ottenere il nome del test per gli screenshot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pytest



from models.conn import db
from models.model import *

from routes.auth import auth as bp_auth

from flask_admin.contrib.sqla import ModelView



app = Flask(__name__)
#-------------------------------------------------------------------------------------------------------------------------
class TestWhatever():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()
        
    def take_screenshot(self):
        test_name = sys._getframe().f_code.co_name
        self.driver.save_screenshot(f'{test_name}.png')

    def test_login_admin_success(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci le credenziali corrette
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("adminpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Verifica che il nome utente sia presente nella pagina
        assert "admin" in self.driver.page_source, "Admin non trovato nella pagina"
        
        # Screenshot del successo del test
        self.take_screenshot()
        
    def test_login_admin_failure(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci credenziali errate
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Verifica la presenza di un messaggio di errore di login
        assert "Please check your login details and try again" in self.driver.page_source, "Messaggio di errore non trovato"
        
        # Screenshot del fallimento del test
        self.take_screenshot()

    def test_logout(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci le credenziali corrette
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("adminpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Fai logout
        self.driver.find_element(By.LINK_TEXT, "Logout").click()
        
        time.sleep(2)  # Attesa per il logout
        
        # Verifica che l'utente è stato disconnesso
        assert "Login" in self.driver.page_source, "Logout non avvenuto correttamente"
        
        # Screenshot del logout
        self.take_screenshot()
    def test_whaterver(self):
        self.driver.save_screenshot(f'{sys._getframe().f_code.co_name}.png') # generates a png file with the name of the test function being called
        
#-------------------------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------------------------

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

admin = Admin(app, name='Admin dashboard', template_mode='bootstrap4')
admin.add_view(ProtectedModelView(User, db.session))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # vecchio codice
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') #os prende e usa la variabile d'ambiente
db.init_app(app)
# nuova classe

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

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
    # return User.query.get(int(user_id))
    return user

#-------------------------------------------------------------------------------------------------------------------------
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
        
@app.route('/dashboard')
@login_required
@user_has_role('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')    
#-------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host="127.0.0.1:5000")
    

