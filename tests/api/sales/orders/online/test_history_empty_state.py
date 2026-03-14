import allure
import pytest
import pytest_check as check
from src.common.user_accounts import UserAccounts
from utils.allure_helper import attach_json
from .base import BaseOnlineOrders

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

class TestSchemeEmptyState(BaseOnlineOrders):
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Check contract for empty online orders history with status: {inputs[status]}")  # Dynamic title
    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_scheme_empty_state(self, online_orders_api, inputs):
        with allure.step(f"Requesting online orders history with status '{inputs['status']}'"):
            parsed_data = self._get_orders(
                online_orders_api,
                page=0,
                limit=40,
                status=inputs["status"])

        with allure.step("Verifying that API returned 0 items"):
            check.equal(len(parsed_data.items), 0, "List of items should be empty")
        with allure.step("Verifying that API returned 0 in totalPages"):
            check.equal(parsed_data.totalPages, 0, "totalPages should be 0")

