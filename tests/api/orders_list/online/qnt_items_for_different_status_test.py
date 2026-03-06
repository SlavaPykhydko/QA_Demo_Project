import pytest
import pytest_check as check

from src.models.orders.online_orders_history import OrdersResponse

test_data = [
    ({"page": 0, "limit": 40, "status": "All"}),
    ({"page": 0, "limit": 40, "status": "Done"}),
    ({"page": 0, "limit": 40, "status": "Cancel"})
]

# Generating good-looking names for reports
test_ids = [f"limit_{d['limit']}_page_{d['page']}_status_{d['status']}" for d in test_data]

@pytest.mark.parametrize("inputs", test_data, ids=test_ids)
def test_quantity_items_for_different_status(online_orders_api, inputs):
    response = online_orders_api.get_online_orders(
        page=inputs["page"],
        limit=inputs["limit"],
        status=inputs["status"]
    )
    parsed_data = OrdersResponse(**response.json())

    check.equal(len(parsed_data.items), parsed_data.totalCount,
                "The number of items is not equal totalCount from response")


