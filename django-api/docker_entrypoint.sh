#!/bin/sh

python -m gunicorn --bind 0.0.0.0:8000 --capture-output --access-logfile '-' --log-file '-' --workers 3 django_api.wsgi:application
