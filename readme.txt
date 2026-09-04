# word_def

## Local development

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q

The test suite uses an in-memory Redis substitute and does not require or
modify a local Redis database.

## Redis and HTTP integration tests

Run integration tests in the isolated Docker Compose project:

docker compose -f compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
docker compose -f compose.test.yml down --volumes

## Production image

Production containers are managed by an external Docker Compose project. Build
the final `production` stage of `Dockerfile`. The image runs Gunicorn as an
unprivileged user and exposes the application on port 34001 by default.

Supported environment variables: REDIS_HOST, REDIS_PORT, REDIS_DB, PORT,
PERMUT_BATCH_SIZE, WEB_CONCURRENCY, GUNICORN_THREADS, GUNICORN_TIMEOUT and
GUNICORN_GRACEFUL_TIMEOUT.

The scripts in `tools/` are administrative operations, not container startup
helpers. Review their data sources and side effects before running them.
