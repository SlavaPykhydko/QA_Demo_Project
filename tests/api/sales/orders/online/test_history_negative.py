from http.client import responses

import allure
import jmespath
import pytest
import pytest_check as check
from tests.api.sales.orders.online.base import BaseOnlineOrders

pytestmark = [
    pytest.mark.negative,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Negative checks")
]


class TestInvalidStatusHandling(BaseOnlineOrders):

    negative_status_data = [
        pytest.param({"status": "Unknown"}, id="status_as_random_string"),
        pytest.param({"status": -1}, id="invalid_status_as_int"),
        pytest.param({"status": ""}, id="invalid_status_as_empty_string"),
        pytest.param({"status": "12345"}, id="status_as_numeric_string")
    ]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and message with invalid status = : {inputs[status]}")
    @pytest.mark.parametrize("inputs", negative_status_data)
    def test_invalid_status_returns_400(self, online_orders_api, inputs):
        response = online_orders_api.get_online_orders(
            page=0,
            limit=40,
            status=inputs["status"],
            raise_for_status=False)

        with allure.step("Check error message"):
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

        online_orders_api.assert_problem_details(response)