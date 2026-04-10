import allure
import pytest
import pytest_check as check

from data.online_orders_constants import LIMIT_40
from data.online_orders_positive_data import STATUS_DATA
from src.common.user_accounts import UserType
from utils.report_helper import github_tc

# All tests in this file will use USER_EMPTY
# Allure grouping for all file
pytestmark = [
    pytest.mark.parametrize("user_session", [UserType.EMPTY], indirect=True),
    pytest.mark.empty_state,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Empty State Validation")
]

class TestSchemeEmptyState:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Check contract with status: {inputs[status]}")  # Dynamic title
    @pytest.mark.parametrize("inputs", STATUS_DATA)
    @github_tc("id-tc-so-oh-es-01")
    def test_scheme_empty_state(self, api, inputs):
        parsed_data = api.online_orders.get_parsed_items(
            page=0,
            limit=LIMIT_40,
            status=inputs["status"])

        with allure.step("Verifying that response returned 0 items"):
            check.equal(len(parsed_data.items), 0, "List of items should be empty")
        with allure.step("Verifying that response returned 0 in totalPages"):
            check.equal(parsed_data.totalPages, 0, "totalPages should be 0")
