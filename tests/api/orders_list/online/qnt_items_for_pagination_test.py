import pytest
import pytest_check as check

from src.models.online_orders_list import OrdersResponse
from tests.api.orders_list.online.counts_and_navigation_parameters_test import count_all_orders_from_db


def test_quantity_items_for_pagination(online_orders_api):
    all_items = []
    for page in [0,1,2]:
        response = online_orders_api.get_online_orders(page=page, limit=10, status="All")
        parsed_data = OrdersResponse(**response.json())
        all_items.extend(parsed_data.items)

    check.equal(len(all_items), count_all_orders_from_db,
                "The number of items is not equal the quantity from db")