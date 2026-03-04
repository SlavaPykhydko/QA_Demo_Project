import json
import jmespath
import requests
from common.logger import get_logger
from requests import Response, HTTPError, Session


class BaseClient:
    def __init__(self, base_url: str, session: Session = None):
        self.base_url = base_url
        self.session = session if session else Session()

        self.logger = get_logger(self.__class__.__name__)

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = None

        # Adding session_id in all requests if it there is in session
        if hasattr(self.session, "api_session_id"):
            # extract current params from kwargs or creating an empty dict
            params = kwargs.get("params", {})
            #Adding our session_id
            params["session_id"] = self.session.api_session_id
            kwargs["params"] = params

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        except HTTPError:
            self._log_error(method, url, response, kwargs)
            raise

    def _log_error(self, method, url, response, kwargs):

        status = response.status_code if response is not None else "NO RESPONSE"
        text = response.text if response is not None else "Connection Error / Timeout"

        error_msg = (
            f"\n{'=' * 40} API ERROR {'=' * 40}\n"
            f"URL: {method} {url}\n"
            f"REQUEST KWARGS: {kwargs}\n"
            f"STATUS CODE: {status}\n"
            f"RESPONSE: {text}\n"
            f"{'=' * 91}"
        )
        self.logger.error(error_msg)

    def _get(self, endpoint, **kwargs):
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
        # try except block was commented because we have already checked it in _request method
        # try:
        data = response.json()
        # except json.decoder.JSONDecodeError:
        #     assert False, f"Response is NOT a json. Response text is  {response.text[:100]}..."

        value = jmespath.search(path, data)

        assert value is not None, f"Path '{path}' not found in JSON: {data}"

        return value