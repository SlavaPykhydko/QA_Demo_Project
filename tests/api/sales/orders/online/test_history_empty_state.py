import allure
import pytest
import pytest_check as check
from src.common.user_accounts import UserAccounts

# All tests in this file will use USER_EMPTY
# Allure grouping for all file
pytestmark = [
    pytest.mark.parametrize("user_session", [UserAccounts.USER_EMPTY], indirect=True),
    pytest.mark.empty_state,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Empty State Validation")
]

class TestSchemeEmptyState:
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Check contract for empty online orders history with status: {inputs[status]}")  # Dynamic title
    @pytest.mark.parametrize("inputs", test_data)
    def test_scheme_empty_state(self, online_orders_api, inputs):
        parsed_data = online_orders_api.get_parsed_items(
            online_orders_api,
            page=0,
            limit=40,
            status=inputs["status"])

        with allure.step("Verifying that API returned 0 items"):
            check.equal(len(parsed_data.items), 0, "List of items should be empty")
        with allure.step("Verifying that API returned 0 in totalPages"):
            check.equal(parsed_data.totalPages, 0, "totalPages should be 0")

