from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dd863c51abd35bb54c0deaba2688887f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.site'  # the three forward slashes indicate a relative path after
# which it's the name of our database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)  # class helping us manage logins
login_manager.login_view = 'login'  # setting the view required to direct it to the correct route
login_manager.login_message_category = 'info'  # this adds a bootstrap class to the message created by the above code

from flaskblog import routes
