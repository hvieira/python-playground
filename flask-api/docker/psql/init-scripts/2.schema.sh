#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname todos <<-EOSQL
    CREATE TABLE todo_task(
    id     varchar(36),
    contents    text,
    PRIMARY KEY(id)
);
EOSQL
