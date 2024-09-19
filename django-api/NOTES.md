# Notes

## Boostrapping project
1. `poetry new django-api`
1. go into the new directory
1. configure `pyproject.toml` with dependencies
1. `poetry lock` 
1. `poetry install`
1. `poetry shell`
1. (because `django_api` directory from poetry conflicts with django startproject) delete dir `django_api`
1. `django-admin startproject django_api`
1. `django-admin startapp store_api`