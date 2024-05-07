from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)

# Configure ckeditor
CKEditor(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class NewPostForm(FlaskForm):
    title = StringField(label="Blog post Title", validators=[DataRequired()])
    subtitle = StringField(label="subtitle", validators=[DataRequired()])
    author_name = StringField(label="Author Name", validators=[DataRequired()])
    image_url = StringField(label="Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField(label="Post Content", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/add-new-post', methods=["GET", "POST"])
def add_new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        author_name = request.form.get('author_name')
        image_url = request.form.get('image_url')
        body = request.form.get('body')
        current_date = date.today().strftime("%B, %d, %Y")

        new_post = BlogPost(title=title, subtitle=subtitle, author=author_name, date=current_date, img_url=image_url,
                            body=body)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form)


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = NewPostForm(
        title=post.title,
        subtitle=post.subtitle,
        image_url=post.img_url,
        author_name=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.image_url.data
        post.author = edit_form.author_name.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))

    return render_template("make-post.html", is_true=True, form=edit_form)


# TODO: delete_post() to remove a blog post from the database
@app.route('/delete')
def delete_post():
    post_id = request.args.get('post_id')
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5003)
