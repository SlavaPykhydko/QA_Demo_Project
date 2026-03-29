# Copilot Instructions

## Scope
- This repository is API test automation for `/api/v2/sales/orders/online`.
- Prioritize `src/`, `tests/api/sales/orders/online/`, `tests/fixtures/`, and `utils/report_helper.py`.
- `src/ui/` and `tests/ui/` are placeholders; avoid proposing UI-first solutions.

## Architecture to Respect
- Pytest composition root is `tests/conftest.py`.
- Fixtures are plugin modules loaded via `pytest_plugins`:
  - `tests/fixtures/config_fixtures.py`
  - `tests/fixtures/db_fixtures.py`
  - `tests/fixtures/api_fixtures.py`
- API boundary:
  - `src/api/base_client.py` (HTTP, retries, timeout, logging, Allure attachments)
  - `src/api/api_client.py` (service aggregator)
  - `src/api/sales/orders/online/online_orders.py` (domain API methods)
- Contract parsing uses Pydantic models in `src/models/orders/online_orders.py`.

## Test Writing Conventions
- Keep file-level `pytestmark` for suite grouping and Allure epic/feature/story.
- Use `pytest_check` soft assertions and wrap logical checks in `allure.step(...)`.
- For negative API checks:
  - call endpoints with `raise_for_status=False`
  - validate RFC-style problem details via `_assert_problem_details(...)`.
- Prefer `api.online_orders._get_json_value(...)` (JMESPath) over ad-hoc JSON traversal.

## Data and Fixtures
- Keep large parametrization datasets in `data/` modules (for example positive/negative/empty-state data files).
- Keep expected-value helpers in test layer (`tests/helpers/online_orders_expected_data.py`), not in runtime `src/` domain modules.
- Reuse existing fixture names (`cfg`, `db`, `user_session`, `api`, `expected_data`) to avoid test breakage.

## Logging, Security, and Reporting
- Do not log secrets or raw auth/session values.
- Reuse centralized masking keys from `src/common/sensitive_keys.py`.
- Keep Allure attachments through `utils/report_helper.py` (`attach_curl`, `attach_json`) so context metadata stays consistent.
- Keep log context fields (`env`, `worker`, `test`, `user`, `req`) intact when changing logger/pytest config.

## Config and Environment Rules
- Supported envs are controlled by pytest option `--env` (`prod`, `stage`).
- Keep fail-fast behavior for missing required config values in `cfg` fixture.
- Config values come from `.env`/CI secrets through `src/common/config.py`.

## Validation Before Finishing Changes
- At minimum run collection for touched suites, for example:
  - `pytest tests/api/sales/orders/online/test_history_positive.py --collect-only -q`
  - `pytest tests/api/sales/orders/online/test_history_negative.py --collect-only -q`
- For HTTP client changes, run retry/timeout checks:
  - `pytest tests/api/test_retry_logic.py -q`

