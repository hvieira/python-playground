# Notes

## Common properties/fields for models
https://docs.djangoproject.com/en/5.1/topics/db/models/#abstract-base-classes

## Extending OR custom django's User
Opted for custom to user UUID as IDs

custom: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

extending - https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#extending-the-existing-user-model

### DRF lookup values conversion
With a ViewSet (`GenericViewSet`, at least) `lookup_field` and `lookup_value_converter` can be set to automatically inject an UUID as the lookup value. But this has a requirement to use path converters - i.e. `use_regex_path=False` in a router

## Model multi column keys (composite primary keys)
This is not supported at the time of writting (08-10-2024) https://code.djangoproject.com/wiki/MultipleColumnPrimaryKeys

The alternative is either:
- https://docs.djangoproject.com/en/5.1/ref/models/constraints/#django.db.models.UniqueConstraint.fields
- [DEPRECATED?] to use unique together constraint - https://docs.djangoproject.com/en/5.1/ref/models/options/#unique-together

## On QuerySet
### reducing number of queries to fetch relations
`prefetch_related` will make a separate subsequent query *for each* of the wanted relation/lookup. This means that it's not possible to retrieve a model with relationships in a single query

## Django Typing
Django has quite a bit of magic - including classes defined at runtime. An example is RelatedManager which fails to be imported.
The following https://github.com/typeddjango/django-stubs seems to be able to add some support for this

## Oauth Lib
This is the best tutorial to get password grant working. Obviously, the password grant is no longer supported from oauth 2.1, but in this case it works to explore using and configuring the lib
https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/getting_started.html

### Validating custom users
With the need to validate that deleted users could not be issued tokens or be generally active with the server,
it is needed to have a custom validation of the user. While subclassing and implementing https://github.com/jazzband/django-oauth-toolkit/blob/3.0.1/oauth2_provider/oauth2_validators.py#L752 would likely work, `authenticate` returns AbstractUser instead of the user model
which is a bit inconvenient. A custom authentication implementation would be needed.
Because the default implementation uses `is_active` field, a custom `save()` can be used to validate that deleted users cannot be active.

## Debugging

### Running a python shell with the django project settings
This will open a shell with the settings loaded: `python manage.py shell`

Then, we can import and test code. For example, to test serializers:
```python
from store_api.serializers import CreateProductRequestSerializer

data = {
    "title": "t",
    "description": "d",
    "price": 1,
    "stock": {
        "default": 10,
        "xl": 3
    }
}

s = CreateProductRequestSerializer(data=data)
s.is_valid()
s.validated_data
```



## Testing
### Test performance
Creating certain models (e.g. users, oauth app) is slow and makes integration tests take a long time - as fixtures for user creation for every test will compound take spent. Whilst I have tried and added a `base_test.py` file with an example of a base class that could have some potential to speed things up a bit, the real solution is based on fixture scoping - e.g. admin users, oauth application can be reused by a testing session. To be able to do this, these fixtures need the
pytest-django db fixtures: `django_db_setup` and `django_db_blocker`, using the latter to unblock the DB and create the entities in the DB.
Using this strategy has allowed to cut test runtimes by more than 50%

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