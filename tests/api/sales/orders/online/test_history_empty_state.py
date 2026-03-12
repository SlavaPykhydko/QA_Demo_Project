import allure
import pytest
import pytest_check as check
import requests
from src.common.online_orders_data import Data
from src.common.user_accounts import UserAccounts
from .base import BaseOnlineOrders

pytestmark = [
    pytest.mark.parametrize("user_session", [UserAccounts.USER_EMPTY], indirect=True),
    pytest.mark.empty_state,
    pytest.mark.regression
]
# Этот тест (и все остальные в файле) запустится под USER_EMPTY

# Группировка для всего файла
@allure.epic("Sales & Orders")
@allure.feature("Orders History")
@allure.story("Empty State Validation")
class TestOnlineOrdersSchemeEmptyState(BaseOnlineOrders):
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

    @allure.tag("regression", "empty_data")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check empty history for status: {inputs[status]}")  # Dynamic title
    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_scheme_empty_state(self, online_orders_api, inputs):
        # online_orders_api внутри себя попросит user_session.
        # user_session увидит, что для него в pytestmark задан USER_EMPTY,
        # и залогинится именно под ним.
        with allure.step(f"Requesting order history with status '{inputs['status']}'"):
            parsed_data = self._get_orders(
                online_orders_api,
                page=0,
                limit=40,
                status=inputs["status"])
            # Прикрепляем JSON сразу после получения, чтобы он всегда был под рукой
            allure.attach(
                parsed_data.model_dump_json(indent=2),
                name="API Response",
                attachment_type=allure.attachment_type.JSON
            )
        with allure.step("Verifying that API returned 0 items"):
            check.equal(len(parsed_data.items), 0, "List of items should be empty")
            check.equal(parsed_data.totalPages, 0, "totalPages should be 0")

