import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


from flask_server.db import dbAlchemy
from flask_server.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.get('/register')
def show_register_page():
    return render_template('auth/register.html')


@bp.post('/register')
def register_user():
    username = request.form['username']
    password = request.form['password']
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        try:
            new_user = User(username=username, password=generate_password_hash(password))
            dbAlchemy.session.add(new_user)
            dbAlchemy.session.commit()
        except IntegrityError:
            error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.show_login_page"))

    flash(error)
    return render_template('auth/register.html')


@bp.get('/login')
def show_login_page():
    return render_template('auth/login.html')


@bp.post('/login')
def login():
    username = request.form['username']
    password = request.form['password']
    error = None

    
    user = dbAlchemy.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user.password, password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = user.id
        return redirect(url_for('index'))

    flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = dbAlchemy.session.get(User, user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.show_login_page'))

        return view(**kwargs)

    return wrapped_view