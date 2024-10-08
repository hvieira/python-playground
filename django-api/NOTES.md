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

## Oauth Lib
This is the best tutorial to get password grant working. Obviously, the password grant is no longer supported from oauth 2.1, but in this case it works to explore using and configuring the lib
https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/getting_started.html

### Validating custom users
With the need to validate that deleted users could not be issued tokens or be generally active with the server,
it is needed to have a custom validation of the user. While subclassing and implementing https://github.com/jazzband/django-oauth-toolkit/blob/3.0.1/oauth2_provider/oauth2_validators.py#L752 would likely work, `authenticate` returns AbstractUser instead of the user model
which is a bit inconvenient. A custom authentication implementation would be needed.
Because the default implementation uses `is_active` field, a custom `save()` can be used to validate that deleted users cannot be active.

## Testing
Creating models when using `@pytest.mark.django_db` is slow and makes integration tests take a long time.

I added a `base_test.py` file with an example of a base class that could have some potential to speed things up a bit.

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