from flaskblog import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)  # P uppercase in Post because here we are

    # referencing the actual post class\ backref author bcoz basically it's making another column in the post table
    # and it can be used to get the User of that post\ lazy bcoz it's taking all the posts made by a single user in
    # one go and it is loading all of them together

    def get_reset_token(self, expires_sec=1800): # these methods are useful for resetting of password by the user
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec) # expires_sec is basically validity time of this serializer object
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  # static method bcoz doesn't depend on object
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)  # here u is lowercase in user.id bcoz we are referencing the table name and its column

    # table name is stored as lowercase by default

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.title}', '{self.date_posted}')"
