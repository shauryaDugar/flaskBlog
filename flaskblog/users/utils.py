import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):  # function to save a profile picture. used in account route
    random_hex = secrets.token_hex(8)  # we want to set a random name to the pic so that it does
    # not clash with our existing database
    _, f_ext = os.path.splitext(form_picture.filename)  # it has a filename attri bcoz it
    # was submitted thru a form and was a valid file
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


def profile_pic_exists(filename):  # function to check if the given profile pic exists in OS
    if os.path.exists(os.path.join(current_app.root_path, 'static/profile pics', filename)):
        return True
    return False


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, click the following link
{url_for('users.reset_token', token=token, _external=True)} 

If you did not make this request, please ignore this email and no changes will be made
'''
    mail.send(msg)

# did _external =True bcoz the link here will be an absolute value not a relative one
