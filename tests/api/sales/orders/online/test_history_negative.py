import allure
import pytest
import pytest_check as check

pytestmark = [
    pytest.mark.negative,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Negative checks")
]


class TestInvalidStatusHandling:

    negative_status_data = [
        pytest.param({"status": "Unknown"}, id="status_as_random_string"),
        pytest.param({"status": -1}, id="status_as_int"),
        pytest.param({"status": ""}, id="status_as_empty_string"),
        pytest.param({"status": "12345"}, id="status_as_numeric_string"),
        pytest.param({"status": "\0"}, id="status_as_null_byte"),
        pytest.param({"status": True}, id="status_as_boolean"),
        pytest.param({"status": "Deleted"}, id="status_as_deleted")
    ]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and problem details with invalid status = : {inputs[status]}")
    @pytest.mark.parametrize("inputs", negative_status_data)
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

    negative_page_data = [
        pytest.param({"page": "Unknown"}, id="page_as_random_string"),
        pytest.param({"page": -1}, id="page_as_negative_int_value",
            marks=[pytest.mark.xfail(reason="BUG: Online orders history. Server error when page=-1", strict=True),
            allure.issue("#Link to Bug #2", "Online orders history. Server error when page=-1"),
            allure.description("⚠️ Expected Bug: Online orders history. Server error when page=-1. Look at task  #2"),]),
        pytest.param({"page": ""}, id="page_as_empty_string"),
        pytest.param({"page": "\0"}, id="page_as_null_byte"),
        pytest.param({"page": True}, id="page_as_boolean")
    ]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking response code and problem details with invalid page = : {inputs[page]}")
    @pytest.mark.parametrize("inputs", negative_page_data)
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
