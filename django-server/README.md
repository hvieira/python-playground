# django-server
Based on the django tutorial, with django rest framework aspects added

## Running
1. start docker containers (backing data services)
`docker-compose up -d`

2. `python manage.py runserver`

## Tests
This uses [pytest-django](https://pytest-django.readthedocs.io/en/latest/) to run the tests.

`pytest` or `pytest -vv`