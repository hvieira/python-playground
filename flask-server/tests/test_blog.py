import pytest

from sqlalchemy import select

from flask_server.models.post import Post
from flask_server.models.user import User
from flask_server.db import dbAlchemy

def test_index(client, app, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data


    auth.register()
    with app.app_context():
        user = get_user_from_username(app)
        post = Post(title='test title', body='whatever', author_id=user.id)
        dbAlchemy.session.add(post)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()
    
        auth.login()
        response = client.get('/')
        assert b'Log Out' in response.data
        assert b'test title' in response.data
        assert b'by test' in response.data
        assert b'whatever' in response.data
        assert 'href="/' + str(post.id) +'/update"' in response.text

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    post_id = None
    with app.app_context():
        auth.register(username = 'testzzz')
        user = get_user_from_username(app, username='testzzz')
        post = Post(title='test title', body='whatever', author_id=user.id)
        dbAlchemy.session.add(post)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

        post_id = post.id

    auth.register()
    auth.login()
    # current user can't modify other user's post
    assert client.post(f'/{post_id}/update').status_code == 403
    assert client.post(f'/{post_id}/delete').status_code == 403
    # current user doesn't see edit link
    assert f'href="/{post_id}/update"' not in client.get('/').text


@pytest.mark.parametrize('path', (
    '/100000000/update',
    '/100000000/delete',
))
def test_actions_on_non_existent_post(client, auth, path):
    auth.register()
    auth.login()
    assert client.post(path).status_code == 404



def test_create(client, auth, app):
    auth.register()
    auth.login()
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'title': 'created', 'body': ''})

    assert response.status_code == 302


def test_update(client, auth, app):
    auth.register()
    auth.login()

    user = get_user_from_username(app)
    post_id = create_post(app, Post(title='Some Test', body='Nice', author_id = user.id))

    assert client.get(f'/{post_id}/update').status_code == 200
    response = client.post(f'/{post_id}/update', data={'title': 'updated', 'body': ''})

    assert response.status_code == 302




def test_create_validate(client, auth):
    auth.register()
    auth.login()
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_update_validate(client, auth, app):
    auth.register()
    auth.login()

    user = get_user_from_username(app)
    post_id = create_post(app, Post(title='Some Test', body='Nice', author_id = user.id))

    response = client.post(f'/{post_id}/update', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    auth.register()
    auth.login()

    user = get_user_from_username(app)
    post_id = create_post(app, Post(title='Some Test', body='Nice', author_id = user.id))

    response = client.post(f'/{post_id}/delete')
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with app.app_context():
        deleted_post = dbAlchemy.session.get(Post, post_id)
        assert deleted_post is None

def get_user_from_username(app, username='test'):
    with app.app_context():
        return dbAlchemy.session.execute(select(User).where(User.username == username)).scalar()

def create_post(app, post):
    post_id = None
    with app.app_context():
        dbAlchemy.session.add(post)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()
        post_id = post.id

    return post_id