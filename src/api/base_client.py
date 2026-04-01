import json
import allure
import jmespath
import os
from time import perf_counter
from enum import Enum
from typing import Any

from src.common.logger import clear_log_context, get_log_context, get_logger, set_log_context
from src.common.sensitive_keys import SENSITIVE_KEYS
from requests import Response, Session
from src.common.mixins.assertions import AssertionsMixin
from utils.report_helper import attach_curl, attach_json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from opentelemetry import trace, propagate
from opentelemetry.trace import Span, format_trace_id, StatusCode

# Отримуємо глобальний трасер
tracer = trace.get_tracer(__name__)

class BaseClient(AssertionsMixin):
    def __init__(self, config, session: Session = None):
        self.base_url = config.BASE_URL
        self.api_version = config.API_VERSION
        self.full_url = f"{self.base_url}{self.api_version}"
        self.session = session if session else Session()
        self.logger = get_logger(self.__class__.__name__)

        # Налаштування Retry Policy та Timeout
        self.default_timeout = config.REQUEST_TIMEOUT
        self.retry_count = config.RETRY_COUNT
        self.backoff_factor = config.BACKOFF_FACTOR

        self._setup_retry_policy()

    def _setup_retry_policy(self):
        """Налаштування автоматичних повторів для нестабільних з'єднань."""
        retry_strategy = Retry(
            total=self.retry_count,  # Кількість спроб
            backoff_factor=self.backoff_factor,  # Пауза: 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],  # Коди, при яких варто спробувати ще раз
            allowed_methods=["GET", "OPTIONS", "HEAD"]  # Ретрай тільки для безпечних (ідемпотентних) запитів
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def _format_json(self, data):
        """Auxiliary method for transformation dict in good-looking string"""
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)

    def _sanitize_for_log(self, data):
        # 1. Якщо це Enum, одразу повертаємо його текстове значення
        if isinstance(data, Enum):
            return data.value

        # 2. Якщо це словник (рекурсивно обробляємо ключі та значення)
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Маскуємо сенситивні дані
                if str(key).lower() in SENSITIVE_KEYS:
                    sanitized[key] = "[MASKED]"
                else:
                    # Рекурсивно чистимо значення (там може бути вкладений Enum або dict)
                    sanitized[key] = self._sanitize_for_log(value)
            return sanitized

        # 3. Якщо це список (наприклад, список товарів або статусів)
        if isinstance(data, list):
            return [self._sanitize_for_log(item) for item in data]

        # 4. Для всіх інших типів (int, float, str) повертаємо як є
        return data

    def _prepare_telemetry(self, span: Span) -> str:
        """Extract trace id from current span and sync it with log context."""
        span_context = span.get_span_context()
        trace_id = format_trace_id(span_context.trace_id)
        set_log_context(request_id=trace_id)
        return trace_id

    def _inject_metadata(self, kwargs: dict[str, Any]) -> None:
        """Inject W3C headers and session_id into outgoing request metadata."""
        headers = kwargs.get("headers", {})
        propagate.inject(headers)
        kwargs["headers"] = headers

        if hasattr(self.session, "api_session_id"):
            params = kwargs.get("params", {})
            params["session_id"] = self.session.api_session_id
            kwargs["params"] = params

    def _record_span_attributes(self, span: Span, kwargs: dict[str, Any]) -> None:
        """Record environment and sanitized request payload details on span."""
        log_context = get_log_context()
        test_nodeid = (
            getattr(self, "test_nodeid", None)
            or log_context.get("test_nodeid_full")
            or log_context.get("test_nodeid")
            or "-"
        )
        test_user = getattr(self, "user_type", None) or log_context.get("user_type") or "-"

        span.set_attribute("test.env", os.environ.get("TARGET_ENV", "prod"))
        span.set_attribute("test.threads", os.environ.get("THREADS", "1"))
        span.set_attribute("test.worker", os.environ.get("PYTEST_XDIST_WORKER", "master"))
        span.set_attribute("test.nodeid", test_nodeid)
        span.set_attribute("test.user", str(test_user))
        # Keep legacy attribute for backward compatibility in existing dashboards.
        span.set_attribute("test.user_type", str(test_user))

        safe_params = self._sanitize_for_log(kwargs.get("params"))
        safe_body = self._sanitize_for_log(kwargs.get("json"))

        if safe_params:
            span.set_attribute("http.request.params", json.dumps(safe_params, ensure_ascii=False))
        if safe_body:
            span.set_attribute("http.request.body", json.dumps(safe_body, ensure_ascii=False))

    def _handle_response_telemetry(self, span: Span, response: Response) -> None:
        """Record response status/body details and finalize span status."""
        span.set_attribute("http.status_code", response.status_code)

        if response.text:
            try:
                res_json = response.json()
                span.add_event(
                    "api_response",
                    attributes={"body": json.dumps(res_json, ensure_ascii=False)[:4000]},
                )
            except Exception:
                span.add_event("api_response_raw", attributes={"body": response.text[:1000]})

        if response.status_code >= 400:
            span.set_status(StatusCode.ERROR, description=f"Status {response.status_code}")
        else:
            span.set_status(StatusCode.OK)

    def _report_to_allure(self, response: Response, trace_id: str, elapsed_ms: int) -> None:
        """Attach request/response artifacts to Allure and add Grafana trace link."""
        attach_curl(response, duration_ms=elapsed_ms)

        if response.text:
            try:
                res_json = response.json()
                attach_json(res_json, name="API Response", response=response, duration_ms=elapsed_ms)
            except Exception:
                pass

        grafana_url = (
            "https://slava17puh.grafana.net/explore?left=%5B%22now-1h%22,"
            "%22now%22,%22Tempo%22,%7B%22query%22:%22"
            f"{trace_id}%22%7D%5D"
        )
        allure.dynamic.link(grafana_url, name=f"📊 Grafana Trace: {trace_id}")


    def _request(self, method, endpoint, raise_for_status=True, **kwargs):
        url = f"{self.full_url}/{endpoint.lstrip('/')}"

        # Main orchestration flow: telemetry -> request -> reporting -> status handling.
        with tracer.start_as_current_span(f"HTTP {method} {endpoint}") as span:
            trace_id = self._prepare_telemetry(span)
            self._inject_metadata(kwargs)
            self._record_span_attributes(span, kwargs)

            self.logger.info(f"Sending {method} to {url}")

            started_at = perf_counter()
            kwargs.setdefault("timeout", self.default_timeout)
            response = None

            try:
                response = self.session.request(method, url, **kwargs)
                elapsed_ms = int((perf_counter() - started_at) * 1000)

                self._handle_response_telemetry(span, response)
                self._report_to_allure(response, trace_id, elapsed_ms)

                if raise_for_status:
                    response.raise_for_status()

                return response

            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, description=str(e))
                if hasattr(self, "_log_error"):
                    self._log_error(method, url, response, kwargs, exception=e)
                raise
            finally:
                clear_log_context("request_id")

    def _log_error(self, method, url, response, kwargs, exception=None):
        status = response.status_code if response is not None else "NO RESPONSE / TIMEOUT"
        #Trying to make the Unsuccessful response (4xx, 5xx) looks good-looking
        try:
            error_body = self._format_json(response.json())
        except Exception:
            error_body = response.text if response is not None else str(exception)

        safe_kwargs = self._sanitize_for_log(kwargs)

        error_msg = (
            f"\n{'=' * 40} API ERROR {'=' * 40}\n"
            f"URL: {method} {url}\n"
            f"REQUEST KWARGS: {safe_kwargs}\n"
            f"STATUS CODE: {status}\n"
            f"RESPONSE BODY: {error_body}\n"
            f"{'=' * 91}"
        )
        self.logger.error(error_msg)

    def _get(self, endpoint, **kwargs):
        # Allure пометит этот метод как вложенный шаг
        with allure.step(f"API Call with params {kwargs}"):
            return self._request("GET", endpoint, **kwargs)

    def _post(self, endpoint, json=None, **kwargs):
        return self._request("POST", endpoint, json=json,  **kwargs)

    def _get_cookie(self, response: Response, cookie_name):
        assert cookie_name in response.cookies, f"Cookie {cookie_name} not found"
        return response.cookies[cookie_name]

    def _get_headers(self, response: Response, header_name):
        assert header_name in response.headers, f"Header {header_name} not found"
        return response.headers[header_name]

    def _get_json_value(self, response: Response, path: str):
        data = response.json()
        value = jmespath.search(path, data)
        return value
