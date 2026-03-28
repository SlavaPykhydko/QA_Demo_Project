import allure
import pytest
import pytest_check as check

from data.online_orders_negative_data import NEGATIVE_PAGE_DATA, NEGATIVE_STATUS_DATA

pytestmark = [
    pytest.mark.negative,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Negative checks")
]


class TestInvalidStatusHandling:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and problem details with invalid status: {inputs[status]}")
    @pytest.mark.parametrize("inputs", NEGATIVE_STATUS_DATA)
    def test_status_field_validation(self, api, inputs):
        response = api.online_orders.get_items(
            page=0,
            limit=40,
            status=inputs["status"],
            raise_for_status=False)

        with allure.step("Check error message"):
            actual_message = api.online_orders._get_json_value(response, "errors.Status[0]")
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

        api.online_orders._assert_problem_details(response)

class TestInvalidPageHandling:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and problem details with invalid page: {inputs[page]}")
    @pytest.mark.parametrize("inputs", NEGATIVE_PAGE_DATA)
    def test_page_field_validation(self, api, inputs):
        response = api.online_orders.get_items(
            page=inputs["page"],
            limit=40,
            status="All",
            raise_for_status=False)

        with allure.step("Check error message"):
            actual_message = api.online_orders._get_json_value(response, "errors.Page[0]")
            check.is_not_none(actual_message,
                              f"Could not find error message in path 'errors.Page[0]'. JSON: {response.text}")
            if actual_message:
                check.is_in(
                    str(inputs['page']),
                    actual_message,
                    f"Value '{inputs['page']}' not found in error message"
                )

                is_valid_template = any(t in actual_message for t in ["is invalid", "is not valid"])
                check.is_true(is_valid_template, f"Unexpected template in message: {actual_message}")

        api.online_orders._assert_problem_details(response)
