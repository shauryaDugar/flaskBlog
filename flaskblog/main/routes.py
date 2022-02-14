from flask import Blueprint, request, render_template
from sqlalchemy import desc

from flaskblog.models import Post
from flaskblog.users.utils import profile_pic_exists

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)  # 1 is the default page here
    posts = Post.query.order_by(desc(Post.date_posted)).paginate(per_page=5, page=page)
    return render_template('home.html', posts=posts, exists=profile_pic_exists)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
