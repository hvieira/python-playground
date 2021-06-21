import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, logging
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            flash('Username is required.')

        if not password:
            flash('Password is required.')

        db = get_db()

        if username_exists(db, username):
            flash(f"User {username} is already registered.")
        else:
            register_user(db, username, password)
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        user = get_user_by_username(db, username)

        print(f"{user} -> {user['password']}")
        print(check_password_hash(user['password'], password))

        if user is None or not check_password_hash(user['password'], password):
            flash('Invalid credentials')
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


def get_user_by_username(db_conn, username):
    user = db_conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    return user


def username_exists(db_conn, username):
    user = get_user_by_username(db_conn, username)
    return user is not None


def register_user(db_conn, username, password):
    db_conn.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    db_conn.commit()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
