import os

import pytest

from src.common.config import DEFAULT_ENV_NAME, envs
from src.common.logger import clear_log_context, get_logger, set_log_context

# Root orchestration node: keep hooks here and load fixture modules as plugins.
pytest_plugins = [
    "tests.fixtures.config_fixtures",
    "tests.fixtures.db_fixtures",
    "tests.fixtures.api_fixtures",
]

# Creating logger for fixture/reports
report_logger = get_logger("TestReport")

def pytest_addoption(parser):
    """ Registration -env flag in pytest."""
    allowed_envs = sorted(name.lower() for name in envs.keys())
    parser.addoption(
        "--env",
        action="store",
        default=DEFAULT_ENV_NAME.lower(),
        type=str.lower,
        choices=allowed_envs,
        help=f"Choose environment: {', '.join(allowed_envs)}"
    )


def pytest_configure(config):
    env_name = config.getoption("--env")
    worker_name = os.getenv("PYTEST_XDIST_WORKER", "main")
    set_log_context(env=env_name, worker=worker_name)


def pytest_sessionfinish(session, exitstatus):
    clear_log_context()


# Generating good-looking names for reports
def pytest_make_parametrize_id(val, argname):
    if argname == "inputs" and isinstance(val, dict):
        # Choosing the important keys for naming
        items = list(val.items())[:3]
        return "-".join([f"{k}_{v}" for k, v in items])

    if argname in ["expected", "allowed_statuses"]:
        return ""

    return None


def pytest_runtest_setup(item):
    set_log_context(test_nodeid=item.nodeid)


def pytest_runtest_teardown(item):
    clear_log_context("test_nodeid")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Running test
    outcome = yield
    report = outcome.get_result()

    # If test failed at the beginning
    if report.when == "call" and report.failed:
        # 1. Getting tests params (if there is a parametrization)
        params = item.callspec.params if hasattr(item, 'callspec') else "No params"

        # 2. Forming a good-looking frame for errors
        error_separator = "!" * 80
        report_logger.error(f"\n{error_separator}")
        report_logger.error(f"TEST FAILED: {item.nodeid}")
        report_logger.error(f"PARAMS: {params}")

        # Adding error text (longrepr - it's what we see in the console)
        if report.longrepr:
            # 3. We get only the most important from the error (reprcrash)
            # or all text if it's a soft checks (pytest-check)
            error_details = report.longreprtext

            # If the log is too long, we can leave only the last N strings
            # where usually there is an error pytest-check
            report_logger.error(f"FAILURE REASON:\n{error_details}")

        report_logger.error(f"{error_separator}\n")

