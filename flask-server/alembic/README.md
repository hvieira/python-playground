# DB migrations
Based on alembic - https://alembic.sqlalchemy.org

## Running migrations
To run for the latest migration version
```sh
alembic upgrade head
```
Read docs for upgrading/downgrading to specific version - https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers