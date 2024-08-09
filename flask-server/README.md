# flask-server
A working sample of a server with Flask

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
 
