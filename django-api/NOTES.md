# Notes

## Common properties/fields for models
https://docs.djangoproject.com/en/5.1/topics/db/models/#abstract-base-classes

## Extending OR custom django's User
Opted for custom to user UUID as IDs

custom: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

extending - https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#extending-the-existing-user-model

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