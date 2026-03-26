# Fixtures Plugins Map

This folder contains pytest plugin modules loaded from `tests/conftest.py` via `pytest_plugins`.

## Plugin split
- `config_fixtures.py`: environment configuration fixture (`cfg`), based on `--env` and `src/common/config.py`.
- `db_fixtures.py`: DB/data preparation fixtures (`db`, `db_orders_counts`, `db_online_orders_map`, `expected_data`).
- `api_fixtures.py`: HTTP/session/auth fixtures (`base_session`, `user_session`, `api`).

## Dependency graph
`cfg` -> `base_session` -> `user_session` -> `api`

`cfg` -> `db` -> (`db_orders_counts`, `db_online_orders_map`, `expected_data`)

## Scopes and lifecycle
- `cfg`: `session`
- `db`: `session`
- `db_orders_counts`: `session`
- `db_online_orders_map`: `session`
- `expected_data`: `session`
- `base_session`: `session`
- `user_session`: `module`
- `api`: `module`

`user_session` mutates headers (`Authorization`, `x-fuser-id`) and sets `session.api_session_id` after login; teardown removes these values.

## Behavior notes
- Auth flow in `user_session`:
  1. `POST /auth/basic` for bearer token
  2. `GET /auth/info/site-user` for `fUserId` and `sessionId`
- `BaseClient._request()` auto-injects `session_id` query param when `session.api_session_id` exists.
- DB checks currently use `FakeDBClient` (not real DB connectivity).

## Local checks
Use these commands after fixture changes:

```bash
pytest tests/api/sales/orders/online --collect-only -q
pytest tests/api/sales/orders/online/test_history_empty_state.py -q --env=prod
```

