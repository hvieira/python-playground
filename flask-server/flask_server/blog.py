from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flask_server.auth import login_required
from flask_server.db import dbAlchemy
from flask_server.models.post import Post
from sqlalchemy import select

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = dbAlchemy.session.execute(select(Post).order_by(Post.created.desc())).scalars()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Post(title=title, body=body, author_id=g.user.id)
            
            dbAlchemy.session.add(post)
            dbAlchemy.session.commit()
            
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    print(post)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            
            dbAlchemy.session.add(post)
            dbAlchemy.session.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.post('/<int:id>/delete')
@login_required
def delete(id):
    post = get_post(id)
    dbAlchemy.session.delete(post)
    dbAlchemy.session.commit()
    return redirect(url_for('blog.index'))


def get_post(id, check_author=True):
    post = dbAlchemy.session.get(Post, id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post