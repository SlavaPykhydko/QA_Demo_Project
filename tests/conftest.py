import os

# СТРОГО В САМОМ ВЕРХУ: Устанавливаем лимиты ДО импортов OTel
# Это гарантирует, что SDK подхватит их при инициализации
os.environ["OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT"] = "65535"
os.environ["OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT"] = "65535"
os.environ["OTEL_EVENT_ATTRIBUTE_VALUE_LENGTH_LIMIT"] = "65535"
import logging

import pytest

from src.common.config import DEFAULT_ENV_NAME, envs
from src.common.logger import clear_log_context, get_logger, set_log_context
from opentelemetry import trace
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider

# Root orchestration node: keep hooks here and load fixture modules as plugins.
pytest_plugins = [
    "tests.fixtures.config_fixtures",
    "tests.fixtures.db_fixtures",
    "tests.fixtures.api_fixtures",
]

# Creating logger for fixture/reports
report_logger = get_logger("TestReport")

_LOG_ATTR_DEFAULTS = {
    "env": "-",
    "worker": "-",
    "test_nodeid": "-",
    "user_type": "-",
    "trace_id": "-",
}
_record_factory_installed = False

# Глобальная переменная для корректного закрытия трейсера
_otel_provider = None

def _install_safe_log_record_factory():
    """Prevent KeyError in pytest log formatting for third-party loggers."""
    global _record_factory_installed
    if _record_factory_installed:
        return

    previous_factory = logging.getLogRecordFactory()

    def safe_factory(*args, **kwargs):
        record = previous_factory(*args, **kwargs)
        for key, default in _LOG_ATTR_DEFAULTS.items():
            if not hasattr(record, key):
                setattr(record, key, default)
        return record

    logging.setLogRecordFactory(safe_factory)
    _record_factory_installed = True


# NOTE: Do not configure TracerProvider here.
# CI/local runs already use `opentelemetry-instrument`, which initializes
# provider/exporters from environment variables.


def _short_test_nodeid(nodeid: str) -> str:
    """Convert full pytest nodeid to a concise `file::test[param]` form."""
    parts = nodeid.split("::")
    if len(parts) < 2:
        return nodeid

    file_name = parts[0].rsplit("/", 1)[-1]
    test_part = parts[-1]
    return f"{file_name}::{test_part}"

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
    global _otel_provider

    # 1. Твои логи и контекст
    _install_safe_log_record_factory()
    env_name = config.getoption("--env") or os.getenv("TARGET_ENV", "prod")
    worker_name = os.getenv("PYTEST_XDIST_WORKER", "main")
    set_log_context(env=env_name, worker=worker_name)

    # 2. Переменные из docker-compose
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    auth_token = os.environ.get("GRAFANA_AUTH_TOKEN")
    service_name = os.environ.get("OTEL_SERVICE_NAME", "python-api-tests")

    # 3. Инициализация OpenTelemetry
    if endpoint and auth_token:
        resource = Resource.create({
            "service.name": service_name,
            "test.worker": worker_name,
            "test.env": env_name
        })

        # Создаем провайдер — он автоматически подтянет лимиты из os.environ,
        # которые мы установили в самом верху файла.
        _otel_provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers={"Authorization": f"Basic {auth_token}"}
        )

        _otel_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(_otel_provider)

        # Включаем перехват запросов
        RequestsInstrumentor().instrument()

        # Печатаем подтверждение (только для воркера 'main' или в -s)
        print(f"\n✅ [OTEL SUCCESS] Worker {worker_name}: Tracing initialized with 64KB limits.")
    else:
        print(f"\n⚠️ [OTEL SKIP] Worker {worker_name}: Missing config.")


def pytest_unconfigure(config):
    """Срабатывает при завершении работы воркера."""
    global _otel_provider
    if _otel_provider:
        worker_name = os.getenv("PYTEST_XDIST_WORKER", "main")
        _otel_provider.shutdown()
        print(f"🚀 [OTEL] Worker {worker_name}: Spans flushed.")


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
    set_log_context(
        test_nodeid=_short_test_nodeid(item.nodeid),
        test_nodeid_full=item.nodeid,
    )


def pytest_runtest_teardown(item):
    clear_log_context("test_nodeid", "test_nodeid_full")


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

