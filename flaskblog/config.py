import os


# the main purpose of this class is to set the configs for the flask app we want to deploy, this includes information
# in the form of attributes like secret key, mail account to be used to send mails and sql database
# for the attributes that are sensitive/private like passwords use environment variables and access them with
# os.environ.get('<variable name>')
class Config:
    SECRET_KEY = 'dd863c51abd35bb54c0deaba2688887f'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.site'  # the three forward slashes indicate a relative path after
    # which it's the name of our database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
