from PIL import Image
import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.models import User, Post
from flaskblog.forms import (RegistrationForm, LoginForm,
                             UpdateAccountForm, PostForm,
                             ResetPasswordForm, RequestResetForm)
from flaskblog import app
from flaskblog import bcrypt, db, mail
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)  # 1 is the default page here
    posts = Post.query.order_by(desc(Post.date_posted)).paginate(per_page=5, page=page)
    return render_template('home.html', posts=posts, exists=profile_pic_exists)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! Please login to continue.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # when we login by typing \account in front of the url it redirects to
            # login but after we login we want to head over to the account page instead of the home page so this piece
            # takes in the argument next and redirects it to the account page

            flash(f'Logged in successfully as {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Enter correct credentials to login!', 'danger')
    return render_template('login.html', title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))


def save_picture(form_picture):  # function to save a profile picture. used in account route
    random_hex = secrets.token_hex(8)  # we want to set a random name to the pic so that it does
    # not clash with our existing database
    _, f_ext = os.path.splitext(form_picture.filename)  # it has a filename attri bcoz it
    # was submitted thru a form and was a valid file
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


def profile_pic_exists(filename):  # function to check if the given profile pic exists in OS
    if os.path.exists(os.path.join(app.root_path, 'static/profile pics', filename)):
        return True
    return False


@app.route("/account", methods=['POST', 'GET'])
@login_required  # making it so that a login is required to view data
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            if current_user.image_file != 'default.jpg' and profile_pic_exists(current_user.image_file):
                os.remove(os.path.join(app.root_path, 'static/profile pics', current_user.image_file))
                # the above two lines delete a profile pic from db if it exists
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account details have been updated successfully!', 'success')
        return redirect(url_for('account'))  # doing this so that the form can be submitted without any problems
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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post was posted successfully', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form,
                           legend='New Post')


@app.route('/post/<int:post_id>')  # route dedicated to each post separately
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title=post.title)


@app.route('/post/<int:post_id>/update', methods=['POST', 'GET'])  # route dedicated to updating a post
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'info')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form=form,
                           legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'info')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id) \
        .order_by(desc(Post.date_posted)) \
        .paginate(per_page=5, page=page)
    return render_template('user.html', title=user.username, user=user, posts=posts)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, click the following link
{url_for('reset_token', token=token, _external=True)} 
    
If you did not make this request, please ignore this email and no changes will be made
'''
    mail.send(msg)
   # did _external =True bcoz the link here will be an absolute value not a relative one


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to you with instructions to reset password", 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('login'))

    return render_template('reset_token.html', form=form, title='Reset Password')
