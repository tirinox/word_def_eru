FROM python:3.11.16-slim-trixie AS dependencies

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_strict.txt .

RUN python -m pip install --no-cache-dir --upgrade pip==26.2.1 \
    && python -m pip install --no-cache-dir -r requirements_strict.txt

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --home-dir /app app \
    && chown app:app /app

FROM dependencies AS runtime

COPY --chown=app:app server.py util.py config.py word_defs.py \
    word_permutation.py word_usage.py gunicorn.conf.py ./

USER app

EXPOSE 34001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ.get('PORT', '34001')}/\", timeout=2)"]

FROM runtime AS test

USER root
COPY requirements.txt requirements-dev.txt ./
RUN python -m pip install --no-cache-dir -r requirements-dev.txt
COPY --chown=app:app pytest.ini test.py ./
COPY --chown=app:app tests ./tests
USER app

CMD ["python", "-m", "pytest", "-q"]

FROM runtime AS production

CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]
