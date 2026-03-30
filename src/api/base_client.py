import json
import allure
import jmespath
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


    def _request(self, method, endpoint, raise_for_status=True, **kwargs):
        url = f"{self.full_url}/{endpoint.lstrip('/')}"
        request_id = kwargs.pop("request_id", uuid4().hex[:8])
        set_log_context(request_id=request_id)
        started_at = perf_counter()

        # Додавання таймауту за замовчуванням, якщо він не переданий явно в тесті
        kwargs.setdefault("timeout", self.default_timeout)

        # Adding session_id in all requests if it there is in session
        if hasattr(self.session, "api_session_id"):
            # extract current params from kwargs or creating an empty dict
            params = kwargs.get("params", {})
            #Adding our session_id
            params["session_id"] = self.session.api_session_id
            kwargs["params"] = params

        safe_params = self._sanitize_for_log(kwargs.get("params"))
        safe_body = self._sanitize_for_log(kwargs.get("json"))
        self.logger.info(
            f"Sending {method} to {url} | Params: {safe_params} | Body: {safe_body}"
        )

        response = None
        try:
            response = self.session.request(method, url, **kwargs)
            elapsed_ms = int((perf_counter() - started_at) * 1000)
            # Attach request metadata and cURL representation to Allure.
            attach_curl(response, duration_ms=elapsed_ms)
            # Trying to make the successful response looks good-looking
            try:
                res_json = response.json()
                self.logger.info(f"Response JSON:\n{self._format_json(res_json)}")
                attach_json(res_json, name="API Response", response=response, duration_ms=elapsed_ms)
            except (JSONDecodeError, ValueError):
                self.logger.info(f"Response is not JSON. Text: {response.text[:200]}...")
            if raise_for_status:
                response.raise_for_status()
            self.logger.info(f"Request completed with status={response.status_code} in {elapsed_ms}ms")
            return response

        except (HTTPError, RequestException) as e:
            # Обробляємо як HTTP помилки, так і помилки з'єднання/таймаути
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
