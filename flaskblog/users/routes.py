import os

from flask import Blueprint, redirect, url_for, flash, render_template, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc

from flaskblog import bcrypt, db
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, profile_pic_exists, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! Please login to continue.", 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title="Register", form=form)


@users.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # when we login by typing \account in front of the url it redirects to
            # login but after we login we want to head over to the account page instead of the home page so this piece
            # takes in the argument next and redirects it to the account page

            flash(f'Logged in successfully as {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Enter correct credentials to login!', 'danger')
    return render_template('login.html', title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('users.login'))


@users.route("/account", methods=['POST', 'GET'])
@login_required  # making it so that a login is required to view data
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            if current_user.image_file != 'default.jpg' and profile_pic_exists(current_user.image_file):
                os.remove(os.path.join(current_app.root_path, 'static/profile pics', current_user.image_file))
                # the above two lines delete a profile pic from db if it exists
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account details have been updated successfully!', 'success')
        return redirect(url_for('users.account'))  # doing this so that the form can be submitted without any problems
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if profile_pic_exists(current_user.image_file):
        image_file = url_for('static', filename='profile pics/' + current_user.image_file)
    else:
        current_user.image_file = 'default.jpg'
        db.session.commit()
        image_file = url_for('static', filename='profile pics/' + 'default.jpg')

    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id) \
        .order_by(desc(Post.date_posted)) \
        .paginate(per_page=5, page=page)
    return render_template('user.html', title=user.username, user=user, posts=posts)


@users.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to you with instructions to reset password", 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@users.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token is invalid or expired', 'warning')
        return redirect(url_for(reset_request))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been reset! Login to continue", 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', form=form, title='Reset Password')
