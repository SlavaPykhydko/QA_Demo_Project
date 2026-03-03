import json
import jmespath
import requests
import logging
from requests import Response


class BaseClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint

        self.logger.info(f"Sending method {method} to  {url}")

        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()

        return response

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
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is NOT a json. Response text is  {response.text[:100]}..."

        value = jmespath.search(path, data)

        assert value in data, f"Path '{path}' not found in JSON: {data}"

        return value