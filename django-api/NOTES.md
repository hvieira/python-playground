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

## Debezium
Debezium bootstrap is relatively easy, just need to check the appropriate docs for config keys for specific source and sink types:
- postgresSQL source: 
    - https://debezium.io/documentation/reference/stable/connectors/postgresql.html
    - https://debezium.io/documentation/reference/stable/operations/debezium-server.html#debezium-source-configuration-properties
- redis stream sink: https://debezium.io/documentation/reference/stable/operations/debezium-server.html#_redis_stream

Important aspects for the config (aside from the docs) that deserve note here, are the prefix for the source topic, which will influence the name of the topic in the sink. In this case of postgres source and Redis sink, it creates a key with type stream with the following format: 
`<prefix>.<schema>.<table_name>`

Additionally, to note that in this project debezium is using the `FileOffsetBackingStore` for storing offsets. This is not a good option for a real world scenario where we want to be "consistent" when sourcing data changes (unless it's in some shared persistent disk). In this case, it would make sense to store the offsets in the source database itself.

The message in resulting stream looks like this (when adding a tag)
```json
{
    "schema": {
        "type": "struct",
        "fields": [
            {
                "type": "struct",
                "fields": [
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.data.Uuid",
                        "version": 1,
                        "field": "id"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "created"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "updated"
                    },
                    {
                        "type": "string",
                        "optional": true,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "deleted"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "name"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "description"
                    }
                ],
                "optional": true,
                "name": "store.public.store_api_tag.Value",
                "field": "before"
            },
            {
                "type": "struct",
                "fields": [
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.data.Uuid",
                        "version": 1,
                        "field": "id"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "created"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "updated"
                    },
                    {
                        "type": "string",
                        "optional": true,
                        "name": "io.debezium.time.ZonedTimestamp",
                        "version": 1,
                        "field": "deleted"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "name"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "description"
                    }
                ],
                "optional": true,
                "name": "store.public.store_api_tag.Value",
                "field": "after"
            },
            {
                "type": "struct",
                "fields": [
                    {
                        "type": "string",
                        "optional": false,
                        "field": "version"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "connector"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "name"
                    },
                    {
                        "type": "int64",
                        "optional": false,
                        "field": "ts_ms"
                    },
                    {
                        "type": "string",
                        "optional": true,
                        "name": "io.debezium.data.Enum",
                        "version": 1,
                        "parameters": {
                            "allowed": "true,last,false,incremental"
                        },
                        "default": "false",
                        "field": "snapshot"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "db"
                    },
                    {
                        "type": "string",
                        "optional": true,
                        "field": "sequence"
                    },
                    {
                        "type": "int64",
                        "optional": true,
                        "field": "ts_us"
                    },
                    {
                        "type": "int64",
                        "optional": true,
                        "field": "ts_ns"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "schema"
                    },
                    {
                        "type": "string",
                        "optional": false,
                        "field": "table"
                    },
                    {
                        "type": "int64",
                        "optional": true,
                        "field": "txId"
                    },
                    {
                        "type": "int64",
                        "optional": true,
                        "field": "lsn"
                    },
                    {
                        "type": "int64",
                        "optional": true,
                        "field": "xmin"
                    }
                ],
                "optional": false,
                "name": "io.debezium.connector.postgresql.Source",
                "field": "source"
            },
            {
                "type": "struct",
                "fields": [
                    {
                        "type": "string",
                        "optional": false,
                        "field": "id"
                    },
                    {
                        "type": "int64",
                        "optional": false,
                        "field": "total_order"
                    },
                    {
                        "type": "int64",
                        "optional": false,
                        "field": "data_collection_order"
                    }
                ],
                "optional": true,
                "name": "event.block",
                "version": 1,
                "field": "transaction"
            },
            {
                "type": "string",
                "optional": false,
                "field": "op"
            },
            {
                "type": "int64",
                "optional": true,
                "field": "ts_ms"
            },
            {
                "type": "int64",
                "optional": true,
                "field": "ts_us"
            },
            {
                "type": "int64",
                "optional": true,
                "field": "ts_ns"
            }
        ],
        "optional": false,
        "name": "store.public.store_api_tag.Envelope",
        "version": 2
    },
    "payload": {
        "before": null,
        "after": {
            "id": "a628467c-5eba-4dca-a5d4-dac9c09b6336",
            "created": "2025-02-11T13:21:54.181982Z",
            "updated": "2025-02-11T13:21:54.181982Z",
            "deleted": null,
            "name": "test-tag",
            "description": "tag for tests"
        },
        "source": {
            "version": "3.0.0.Final",
            "connector": "postgresql",
            "name": "store",
            "ts_ms": 1739280114182,
            "snapshot": "false",
            "db": "store",
            "sequence": "[\\"1663012064\\",\\"1663243984\\"]",
            "ts_us": 1739280114182483,
            "ts_ns": 1739280114182483000,
            "schema": "public",
            "table": "store_api_tag",
            "txId": 25883,
            "lsn": 1663243984,
            "xmin": null
        },
        "transaction": null,
        "op": "c",
        "ts_ms": 1739280114595,
        "ts_us": 1739280114595387,
        "ts_ns": 1739280114595387761
    }
}
```


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