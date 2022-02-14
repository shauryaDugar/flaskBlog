from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config


mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()  # class helping us manage logins
login_manager.login_view = 'users.login'  # setting the view required to direct it to the correct route
login_manager.login_message_category = 'info'  # this adds a bootstrap class to the message created by the above code


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)  # this piece is useful for setting configurations of this app to the object passed
    # as argument. This is particularly useful because many times we can inherit configurations.
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    mail.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app