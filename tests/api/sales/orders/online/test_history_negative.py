import allure
import jmespath
import pytest
import pytest_check as check

from src.common.user_accounts import UserAccounts
from tests.api.sales.orders.online.base import BaseOnlineOrders

pytestmark = [
    pytest.mark.negative,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Negative checks")
]


class TestResponseCode(BaseOnlineOrders):

    negative_status_data = [
        pytest.param({"status": "Unknown"}, id="invalid_status_as_Unknown")
        # pytest.param({"status": -1}, id="invalid_status_as_int"),
        # pytest.param({"status": None}, id="invalid_status_as_None"),
        # pytest.param({"status": ""}, id="invalid_status_as_empty_string")
    ]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and message with invalid status = : {inputs[status]}")
    @pytest.mark.parametrize("inputs", negative_status_data)
    def test_response_code_400(self, online_orders_api, inputs):
        response = online_orders_api.get_online_orders(
            status=inputs["status"],
            raise_for_status=False)

        actual_message = online_orders_api._get_json_value(response, "errors.Status[0]")
        check.is_not_none(actual_message,
                          f"Could not find error message in path 'errors.Status[0]'. JSON: {response.text}")
        if actual_message:
            check.is_in(
                str(inputs['status']),
                actual_message,
                f"Value '{inputs['status']}' not found in error message"
            )

            is_valid_template = any(t in actual_message for t in ["is invalid", "is not valid"])
            check.is_true(is_valid_template, f"Unexpected template in message: {actual_message}")

        check.equal(response.status_code, 400, "Expected status code 400")


