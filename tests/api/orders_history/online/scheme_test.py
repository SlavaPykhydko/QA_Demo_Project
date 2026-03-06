import pytest
from src.models.orders.online_orders_history import OrdersResponse

test_data = [
    ({"status": "All"}),
    ({"status": "Done"}),
    ({"status": "Cancel"})
]

# Generating good-looking names for reports
test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

@pytest.mark.parametrize("inputs", test_data, ids=test_ids)
def test_scheme(online_orders_api, inputs):
    response = online_orders_api.get_online_orders(page=0, limit=40, status=inputs["status"])
    OrdersResponse(**response.json())