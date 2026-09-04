# AGENTS.md

## Purpose

Modernize this repository incrementally while preserving its public HTTP API,
Redis data formats, and existing business algorithms. Prefer small, reviewable
changes backed by characterization tests.

## Repository map

- `server.py` defines the Flask application and all public HTTP routes.
- `word_defs.py` stores and edits word definitions in Redis.
- `word_usage.py` stores usage counters and best scores in Redis.
- `word_permutation.py` stores and samples permutation buckets from Redis.
- `util.py` contains shared Redis, HTTP response, validation, and collection
  helpers.
- `config.py` contains runtime defaults.
- `gunicorn.conf.py` contains production WSGI defaults.
- `compose.test.yml` defines the isolated Redis integration-test environment;
  production orchestration lives outside this repository.
- `tools/` contains offline and administrative scripts; some scripts read or
  mutate production-shaped Redis/MySQL data.
- `data/` contains large source and generated datasets. Treat their schemas and
  encodings as compatibility-sensitive.
- `requirements.txt` is the human-maintained direct dependency list;
  `requirements_strict.txt` is the deployment snapshot currently consumed by
  the Docker build.

## Compatibility contract

Unless the user explicitly approves a migration, preserve all of the following:

- Route paths, accepted HTTP methods, path parameters, and request JSON fields.
- Response status codes, JSON field names, nesting, value types, and the
  `result: ok|error` envelope.
- Word normalization, definition ordering and IDs, permutation bucket names,
  sorting/random-sampling behavior, usage-rate calculations, and score rules.
- Redis key prefixes and key construction: `word_def_`, `wus_`, `wms_`,
  `wperm_`, and `max_word_usage`.
- Stored JSON/list/string formats and compatibility with existing Redis data.
- CLI script inputs, outputs, environment-variable names, and side effects.

Internal refactoring is welcome when these observable behaviors remain the
same. Do not combine a dependency upgrade, behavior change, and structural
refactor in one change.

## Defects that require discussion first

Do not silently fix a defect when the fix could change API behavior, persisted
data, ordering/randomness, concurrency semantics, deployment topology, or an
administrative script's side effects. Instead:

1. Reproduce or point to concrete evidence.
2. Describe impact and affected callers/data.
3. Propose the smallest compatible fix and a rollback or migration path.
4. Add a characterization/regression test when possible.
5. Wait for explicit approval before implementing the behavior change.

Security or data-loss risks should be reported immediately. Avoid printing
credentials, proxy URLs, database contents, or full definition datasets in
logs and review output.

## Development workflow

1. Inspect `git status` and preserve unrelated user changes.
2. Read the complete call path and relevant administrative scripts before
   editing shared modules such as `util.py` or `config.py`.
3. Capture current behavior with tests before refactoring it.
4. Make the smallest coherent change; prefer explicit imports and type hints
   only where they do not introduce import cycles or runtime changes.
5. Run focused checks, then the broader checks below.
6. Review the diff for API, Redis-schema, dependency, and operational changes.

Do not run deployment, upload, database migration, cleanup, Redis `SAVE`, or
container-removal commands merely as verification. Those operations require an
explicit task and confirmed target environment.

## Checks

Syntax-only check (does not require Redis):

```sh
.venv/bin/python -m compileall -q server.py util.py word_defs.py \
  word_permutation.py word_usage.py tools
```

Test suite (requires `pytest`; several existing tests also require a disposable
Redis instance configured by `config.py` and mutate test keys):

```sh
.venv/bin/python -m pytest -q
```

Before running Redis-backed tests, confirm that the configured database is safe
to mutate. New unit tests should prefer a fake Redis implementation or mocks so
they are deterministic and isolated.

Run Redis integration tests only through the dedicated Compose project:

```sh
docker compose -f compose.test.yml up --build --abort-on-container-exit \
  --exit-code-from tests
docker compose -f compose.test.yml down --volumes
```

For API work, add Flask test-client coverage for both success and error response
shapes. For Redis work, test both empty state and legacy stored representations.

## Dependency policy

- Verify proposed versions against primary project documentation or PyPI and
  review release notes for every direct dependency jump.
- Upgrade one dependency family at a time, with tests, rather than blindly
  refreshing the entire strict snapshot.
- Keep runtime and development/tooling dependencies distinguishable.
- Regenerate the strict deployment snapshot from declared direct dependencies;
  do not hand-edit transitive pins without documenting why.
- Pin Docker base images and Redis images to reviewed versions (and digests when
  reproducibility is required); never introduce a floating `latest` tag.
- Treat major upgrades of Redis clients, Pillow, MySQL Connector, Python, or the
  production server as migration work requiring explicit review.

## Definition of done

A modernization change is complete only when focused tests pass, syntax checks
pass, the diff contains no unrelated edits, compatibility-sensitive behavior is
unchanged or explicitly approved, and documentation/dependency snapshots match
the actual runtime.
