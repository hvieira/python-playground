# flask-server
A working sample of a server with Flask

## Tasks
- Setup postgresSQL as DB
- Check Alembic for db migrations and see if its useful and use it (if it is good)
- Create an API with separate auth to the tutorial. Use posts and users all the same
    - (to simplify) get blackbox tokens for auth with user credentials - https://www.oauth.com/oauth2-servers/access-tokens/password-grant/. Allow users to register for this
    - store the tokens in db, but use redis as a cache for this, with proper TTL and so on
- Have a react app working with the backend. Try https://pypi.org/project/flask-vite/

## Running
After activating the virtual env with:
```sh
poetry shell
```

(if the dependencies have not been installed yet)
```sh
poetry init
```

run flask
```sh
poetry run flask --app flask_server/main.py run
```

## Tests
After activating the virtual env:
```sh
pytest
```

Run with coverage:
```sh
poetry run coverage run --source=flask_server -m pytest  
poetry run coverage report
```
 
