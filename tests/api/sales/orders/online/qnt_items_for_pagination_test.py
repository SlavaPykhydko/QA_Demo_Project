import pytest_check as check

from src.models.orders_history.online_orders_history import OrdersResponse



def test_quantity_items_for_pagination(online_orders_api, db_counts):
    all_items = []
    for page in [0,1,2]:
        response = online_orders_api.get_online_orders(page=page, limit=10, status="All")
        parsed_data = OrdersResponse(**response.json())
        all_items.extend(parsed_data.items)

    check.equal(len(all_items), db_counts["all"],
                "The number of items is not equal the quantity from db")