import json
import allure
import jmespath
import os
from time import perf_counter
from uuid import uuid4
from enum import Enum

from src.common.logger import clear_log_context, get_logger, set_log_context
from src.common.sensitive_keys import SENSITIVE_KEYS
from requests import Response, Session
from requests.exceptions import HTTPError, JSONDecodeError, RequestException
from src.common.mixins.assertions import AssertionsMixin
from utils.report_helper import attach_curl, attach_json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from opentelemetry import trace, propagate
from opentelemetry.trace import format_trace_id, StatusCode

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


    # def _request(self, method, endpoint, raise_for_status=True, **kwargs):
    #     # Починаємо новий "Span" (етап) для кожного запиту
    #     with tracer.start_as_current_span(f"HTTP {method} {endpoint}") as span:
    #         url = f"{self.full_url}/{endpoint.lstrip('/')}"
    #
    #         # Отримуємо Trace ID від OpenTelemetry (у форматі hex)
    #         span_context = span.get_span_context()
    #         trace_id = format_trace_id(span_context.trace_id)
    #
    #         # Оновлюємо твій лог-контекст існуючим Trace ID
    #         # Тепер твій request_id у логах буде дорівнювати Trace ID
    #         # request_id = kwargs.pop("request_id", uuid4().hex[:8])
    #         set_log_context(request_id=trace_id)
    #
    #         # Додаємо W3C стандартні хедери (traceparent) до запиту автоматично
    #         headers = kwargs.get("headers", {})
    #         propagate.inject(headers)
    #         kwargs["headers"] = headers
    #
    #         started_at = perf_counter()
    #
    #         # Додавання таймауту за замовчуванням, якщо він не переданий явно в тесті
    #         kwargs.setdefault("timeout", self.default_timeout)
    #
    #         # Adding session_id in all requests if it there is in session
    #         if hasattr(self.session, "api_session_id"):
    #             # extract current params from kwargs or creating an empty dict
    #             params = kwargs.get("params", {})
    #             #Adding our session_id
    #             params["session_id"] = self.session.api_session_id
    #             kwargs["params"] = params
    #
    #         # Готуємо безпечні дані для логів та Jaeger
    #         safe_params = self._sanitize_for_log(kwargs.get("params"))
    #         safe_body = self._sanitize_for_log(kwargs.get("json"))
    #
    #         # --- ДОДАЄМО ПАРАМЕТРИ В JAEGER ТУТ ---
    #         if safe_params:
    #             span.set_attribute("request.params", json.dumps(safe_params, ensure_ascii=False))
    #         if safe_body:
    #             span.set_attribute("request.body", json.dumps(safe_body, ensure_ascii=False))
    #         # --------------------------------------
    #
    #         self.logger.info(
    #             f"Sending {method} to {url} | Params: {safe_params} | Body: {safe_body}"
    #         )
    #
    #         response = None
    #         try:
    #             response = self.session.request(method, url, **kwargs)
    #             elapsed_ms = int((perf_counter() - started_at) * 1000)
    #             # 1. Додаємо корисні теги (Attributes)
    #             span.set_attribute("http.method", method)
    #             span.set_attribute("http.url", url)
    #             span.set_attribute("http.status_code", response.status_code)
    #
    #             # --- ДОДАЄМО SUCCESS RESPONSE BODY В JAEGER ---
    #             if response.status_code < 400:
    #                 try:
    #                     res_json = response.json()
    #                     # Робимо рядок із JSON
    #                     res_text = json.dumps(res_json, ensure_ascii=False)
    #
    #                     # Обмежуємо розмір (наприклад, до 3000 символів), щоб не перевантажувати Jaeger
    #                     if len(res_text) > 3000:
    #                         res_text = res_text[:3000] + "... [TRUNCATED FOR JAEGER]"
    #
    #                     # Додаємо як подію (Event), так само як ми робили для помилок
    #                     span.add_event("api_response_data", attributes={
    #                         "response.body": res_text
    #                     })
    #                 except (JSONDecodeError, ValueError):
    #                     # Якщо це не JSON, беремо перші 500 символів тексту
    #                     span.set_attribute("response.raw_text", response.text[:500])
    #
    #             # 2. Якщо статус код >= 400, позначаємо спан як помилку
    #             if response.status_code >= 400:
    #                 span.set_status(StatusCode.ERROR, description=response.reason)
    #
    #                 try:
    #                     error_json = response.json()
    #
    #                     # 1. Витягуємо головний заголовок помилки (наприклад, "One or more validation errors occurred.")
    #                     error_title = error_json.get("title", "Validation Error")
    #
    #                     # 2. Формуємо зручний текст із деталями помилок
    #                     # Перетворюємо {"Status": ["The value '-1' is invalid."]} у зрозумілий рядок
    #                     validation_details = ""
    #                     if "errors" in error_json:
    #                         details = []
    #                         for field, messages in error_json["errors"].items():
    #                             details.append(f"{field}: {', '.join(messages)}")
    #                         validation_details = " | ".join(details)
    #
    #                     # 3. Додаємо подію в Jaeger з усіма деталями
    #                     span.add_event("api_validation_failed", attributes={
    #                         "error.title": error_title,
    #                         "error.fields": validation_details,
    #                         "error.full_response": json.dumps(error_json, ensure_ascii=False)
    #                     })
    #
    #                     # Додатково можна винести title в атрибути для швидкого перегляду
    #                     span.set_attribute("error.message", error_title)
    #
    #                 except Exception:
    #                     # Якщо це не JSON або сталась помилка парсингу — пишемо сирий текст
    #                     span.set_attribute("error.raw_payload", response.text[:500])
    #
    #             # --- ОСЬ ТУТ ДОДАЄМО ПОСИЛАННЯ НА JAEGER ---
    #             # Ми додаємо його одразу, щоб воно було в Allure незалежно від успіху запиту
    #             allure.dynamic.link(f"http://localhost:16686/trace/{trace_id}", name=f"🔎 Trace: {trace_id}")
    #             # ------------------------------------------
    #             # Attach request metadata and cURL representation to Allure.
    #             attach_curl(response, duration_ms=elapsed_ms)
    #             # Trying to make the successful response looks good-looking
    #             try:
    #                 res_json = response.json()
    #                 self.logger.info(f"Response JSON:\n{self._format_json(res_json)}")
    #                 attach_json(res_json, name="API Response", response=response, duration_ms=elapsed_ms)
    #             except (JSONDecodeError, ValueError):
    #                 self.logger.info(f"Response is not JSON. Text: {response.text[:200]}...")
    #             if raise_for_status:
    #                 response.raise_for_status()
    #             self.logger.info(f"Request completed with status={response.status_code} in {elapsed_ms}ms")
    #             return response
    #
    #         except (HTTPError, RequestException) as e:
    #             # Обробляємо як HTTP помилки, так і помилки з'єднання/таймаути
    #             self._log_error(method, url, response, kwargs, exception=e)
    #             raise
    #         finally:
    #             clear_log_context("request_id")
    def _request(self, method, endpoint, raise_for_status=True, **kwargs):
        url = f"{self.full_url}/{endpoint.lstrip('/')}"

        # 1. Получаем текущий спан или создаем валидный, чтобы не было "нулей"
        span = trace.get_current_span()
        if not span.get_span_context().is_valid:
            span = tracer.start_span(f"HTTP {method} {endpoint}")

        with trace.use_span(span, end_on_exit=True):
            span_context = span.get_span_context()
            trace_id = format_trace_id(span_context.trace_id)

            # Синхронизируем Trace ID с логами
            set_log_context(request_id=trace_id)

            # Проброс заголовков трассировки
            headers = kwargs.get("headers", {})
            propagate.inject(headers)
            kwargs["headers"] = headers

            # --- ВОЗВРАЩАЕМ SESSION_ID (Тот самый потерянный блок) ---
            if hasattr(self.session, "api_session_id"):
                params = kwargs.get("params", {})
                params["session_id"] = self.session.api_session_id
                kwargs["params"] = params
            # -------------------------------------------------------

            # Подготовка данных для атрибутов
            span.set_attribute("test.env", os.environ.get("TARGET_ENV", "prod"))
            span.set_attribute("test.threads", os.environ.get("THREADS", "1"))
            if hasattr(self, "user_type"):
                span.set_attribute("test.user_type", self.user_type)

            safe_params = self._sanitize_for_log(kwargs.get("params"))
            safe_body = self._sanitize_for_log(kwargs.get("json"))

            if safe_params:
                span.set_attribute("http.request.params", json.dumps(safe_params, ensure_ascii=False))
            if safe_body:
                span.set_attribute("http.request.body", json.dumps(safe_body, ensure_ascii=False))

            self.logger.info(f"Sending {method} to {url} | Params: {safe_params}")

            started_at = perf_counter()
            kwargs.setdefault("timeout", self.default_timeout)
            response = None

            try:
                # САМ ЗАПРОС
                response = self.session.request(method, url, **kwargs)
                elapsed_ms = int((perf_counter() - started_at) * 1000)

                # Атрибуты ответа
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.duration_ms", elapsed_ms)

                # 3. Capture Response Body как Event
                if response.text:
                    try:
                        res_payload = response.json()
                        res_text = json.dumps(res_payload, ensure_ascii=False, indent=2)
                    except:
                        res_text = response.text

                    span.add_event("api_response", attributes={
                        "body": res_text[:4000]
                    })

                # 4. Логика статусов
                if response.status_code >= 400:
                    span.set_status(StatusCode.ERROR, description=f"HTTP {response.status_code}")
                else:
                    span.set_status(StatusCode.OK)

                # 5. Ссылка на Grafana для Allure
                grafana_url = (
                    f"https://slava17puh.grafana.net/explore?left=%5B%22now-1h%22,%22now%22,%22Tempo%22,"
                    f"%7B%22query%22:%22{trace_id}%22%7D%5D"
                )
                allure.dynamic.link(grafana_url, name=f"📊 Grafana Trace: {trace_id}")

                # Allure Attachments
                attach_curl(response, duration_ms=elapsed_ms)

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
