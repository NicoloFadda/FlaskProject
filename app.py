import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user
from flask_admin import Admin   # nuovo
from flask_admin.contrib.sqla import ModelView

from models.conn import db
from models.model import *

from routes.auth import auth as bp_auth
from routes.default import default as bp_default


from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # vecchio codice
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') #os prende e usa la variabile d'ambiente

app.register_blueprint(bp_default)
app.register_blueprint(bp_auth, url_prefix='/auth')

db.init_app(app)
migrate = Migrate(app, db)

#-------------------------------------------------------------------------------------------------------------------------
class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

admin = Admin(app, name='Admin dashboard', template_mode='bootstrap4')
admin.add_view(ProtectedModelView(User, db.session))
#-------------------------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------------------------


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

#-------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
    

