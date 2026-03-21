import json
from statistics import mean

import allure
import jmespath
from pytest_check import check

from src.common.logger import get_logger
from requests import Response, Session
from requests.exceptions import HTTPError, JSONDecodeError


class BaseClient:
    def __init__(self, cfg, session: Session = None):
        self.config = cfg
        self.base_url = cfg.BASE_URL
        self.api_version = cfg.API_VERSION
        self.full_url = f"{self.base_url}{self.api_version}"
        self.session = session if session else Session()
        self.logger = get_logger(self.__class__.__name__)

    def _format_json(self, data):
        """Auxiliary method for transformation dict in good-looking string"""
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)


    def _request(self, method, endpoint, raise_for_status=True, **kwargs):
        url = f"{self.full_url}/{endpoint.lstrip('/')}"

        # Adding session_id in all requests if it there is in session
        if hasattr(self.session, "api_session_id"):
            # extract current params from kwargs or creating an empty dict
            params = kwargs.get("params", {})
            #Adding our session_id
            params["session_id"] = self.session.api_session_id
            kwargs["params"] = params

        self.logger.info(f"Sending {method} to {url} | Params: {kwargs.get('params')} | Body: {kwargs.get('json')}")

        response = None
        try:
            response = self.session.request(method, url, **kwargs)
            # Trying to make the successful response looks good-looking
            try:
                res_json = response.json()
                self.logger.info(f"Response JSON:\n{self._format_json(res_json)}")
            except (JSONDecodeError, ValueError):
                self.logger.info(f"Response is not JSON. Text: {response.text[:200]}...")
            if raise_for_status:
                response.raise_for_status()
            return response

        except HTTPError:
            self._log_error(method, url, response, kwargs)
            raise


    def _log_error(self, method, url, response, kwargs):
        status = response.status_code if response is not None else "NO RESPONSE"
        #Trying to make the Unsuccessful response (4xx, 5xx) looks good-looking
        try:
            error_body = self._format_json(response.json())
        except Exception:
            error_body = response.text if response is not None else "Connection Error"

        error_msg = (
            f"\n{'=' * 40} API ERROR {'=' * 40}\n"
            f"URL: {method} {url}\n"
            f"REQUEST KWARGS: {kwargs}\n"
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
