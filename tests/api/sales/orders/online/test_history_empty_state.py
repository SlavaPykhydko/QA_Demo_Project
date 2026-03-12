import pytest
import pytest_check as check
import requests
from src.common.online_orders_data import Data
from src.common.test_users import TestUsers
from .base import BaseOnlineOrders
from concurrent.futures import ThreadPoolExecutor


pytestmark = [
    pytest.mark.parametrize("user_session", [TestUsers.USER_EMPTY], indirect=True),
    pytest.mark.empty_state,
    pytest.mark.regression
]
# Этот тест (и все остальные в файле) запустится под USER_EMPTY

class TestOnlineOrdersSchemeEmptyState(BaseOnlineOrders):
    test_data = [
        ({"status": "All"})
        # ({"status": "Done"}),
        # ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_scheme_empty_state(self, online_orders_api, inputs):
        # online_orders_api внутри себя попросит user_session.
        # user_session увидит, что для него в pytestmark задан USER_EMPTY,
        # и залогинится именно под ним.
        parsed_data = self._get_orders(
            online_orders_api,
            page=0,
            limit=40,
            status=inputs["status"])

        assert len(parsed_data.items) == 0
        assert parsed_data.totalPages == 0

