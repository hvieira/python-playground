# DB migrations
Based on alembic - https://alembic.sqlalchemy.org

## Create migrations
`alembic revision -m <description>`

## Running migrations
To run for the latest migration version
```sh
alembic upgrade head
```
Read docs for upgrading/downgrading to specific version - https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers

## Thoughts on best practices

### Revision naming
Since revisions names begin, at least with the default template, with "random" strings, the best thing to do is to use the
`file_template` config in `alembic.ini` to define names based on dates, for example. This way, revisions are neatly ordered.