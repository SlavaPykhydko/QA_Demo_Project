# AGENTS.md

## Scope and intent
- This repo is an API test automation framework (Python + Pytest + Allure) focused on `/api/v2/sales/orders/online`.
- Main implementation areas: `src/` (clients/models/config), `tests/api/sales/orders/online/` (test suites), `utils/report_helper.py` (Allure helpers).
- `src/ui/` and `tests/ui/` currently contain only placeholders; most real work is in API tests.

## Architecture map (read these first)
- `tests/conftest.py`: central composition root for CLI flags, environment config, auth session bootstrap, and `ApiClient` fixture wiring.
- `src/common/config.py`: environment selection (`PROD`/`STAGE`) and env-var contract loaded via `.env`.
- `src/api/base_client.py`: shared HTTP layer (`_request`, status handling, session-id query injection, JSON/JMESPath helpers).
- `src/api/api_client.py` + `src/api/sales/orders/online/online_orders.py`: service boundary; `ApiClient` exposes domain APIs, `OnlineOrdersAPI` implements endpoint methods.
- `src/models/orders/online_orders.py`: Pydantic contract models used by `get_parsed_items()`.
- `src/database/db_client.py`: currently uses `FakeDBClient` in fixtures; real `DBClient` skeleton exists but is not active.

## Data flow and test layering
- Session flow in `tests/conftest.py`: `base_session` (common headers) -> `user_session` (login + `/auth/info/site-user`) -> `api` fixture.
- `BaseClient._request()` auto-adds `session_id` query param when `session.api_session_id` exists.
- Most tests call `api.online_orders.get_items(...)` or `get_parsed_items(...)`; parsed calls enforce Pydantic schema validation.
- DB-backed assertions rely on fixture data from `FakeDBClient` (`db_orders_counts`, `db_online_orders_map`).

## Local run and CI workflows
- Install deps: `pip install -r requirements.txt`.
- Pytest defaults are in `pytest.ini` (`-v -s --tb=short` and markers list).
- Common local runs:
  - `pytest tests/api/sales/orders/online --env=prod -m smoke -n 2`
  - `pytest tests/api/sales/orders/online --env=stage -m "regression and not smoke" -n 2`
  - `pytest tests/api/sales/orders/online/test_history_performance.py --env=prod -m performance`
- Docker path (`docker-compose.yml`) runs smoke -> regression -> performance sequentially and writes JUnit XML into `junit-reports/`.
- CI path (`.github/workflows/api_tests.yml`) builds Docker, runs compose tests, publishes Allure report to `gh-pages`, and sends Telegram summary from aggregated JUnit stats.

## Project-specific conventions to preserve
- Use `pytest_check` soft assertions (`check.*`) with `allure.step(...)` blocks (see `tests/api/sales/orders/online/test_history_positive.py`).
- Keep file-level `pytestmark` for suite grouping (`positive/negative/performance/empty_state`, `regression`, Allure epic/feature/story).
- For negative tests, call endpoint with `raise_for_status=False` and validate RFC-style problem details through `AssertionsMixin._assert_problem_details()`.
- Reuse `BaseClient` helpers (`_get_json_value` with JMESPath) instead of ad-hoc JSON traversal.
- Preserve sensitive-data masking behavior in `utils/report_helper.py` when changing logging/attachments.

## Integration and secrets touchpoints
- Required secrets are defined by `.env.example` and consumed by `src/common/config.py`, `docker-compose.yml`, and CI workflow env mapping.
- Auth depends on `/auth/basic` and `/auth/info/site-user`; order-history calls require bearer token + `x-fuser-id` header + `session_id` query.
- Allure artifacts are written to `allure-results/`; daily logs go to `logs/automation_YYYY-MM-DD.log` via `src/common/logger.py`.

