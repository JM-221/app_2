from flask import Flask
#from flask.ext.login import LoginManager
from flask_login import LoginManager
from .models import db

from flask_login import AnonymousUserMixin


class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.name = "Guest"
    self.password = "123"
    self.email = "akj@jhgj"

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    #with app.app_context():
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonymous


    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    app.app_context().push()
    return app