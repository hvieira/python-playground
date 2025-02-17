FROM python:3.10-slim AS base
ENV  POETRY_VERSION=1.8.5 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get -y install libpq-dev gcc
 
 
FROM base AS builder

RUN --mount=type=cache,target=/root/.cache \
  pip install "poetry==$POETRY_VERSION"
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN --mount=type=cache,target=$POETRY_HOME/pypoetry/cache \
poetry install --no-dev


FROM base AS production
EXPOSE 8000

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /app

# copy supporting files
COPY manage.py manage.py
COPY docker_entrypoint.sh docker_entrypoint.sh 
# Make the entrypoint script executable
RUN chmod +x  docker_entrypoint.sh

# copy application code
COPY django_api django_api
COPY store_async_jobs store_async_jobs
COPY store_api store_api


CMD ["/app/docker_entrypoint.sh"]