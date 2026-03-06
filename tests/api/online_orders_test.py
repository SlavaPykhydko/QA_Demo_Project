import pytest
import pytest_check as check

from src.models.online_orders_list import OrdersResponse

# We need to get this data from db,
# but we don't have this opportunity now, so we just use data from response
count_all_orders_from_db = 21
count_done_orders_from_db = 19
count_cancel_orders_from_db = 2

# Defining test data (input parameters, expected results)
test_data = [
    # 1. All orders in one page
    (
        {"page": 0, "limit": 40, "status": "All"},
        {"totalCount": count_all_orders_from_db, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
    ),
    # 2. The first page with limit=10
    (
        {"page": 0, "limit": 10, "status": "All"},
        {"totalCount": count_all_orders_from_db, "totalPages": 3, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": True}
    ),
    # 3. The last page with limit=10
    (
        {"page": 2, "limit": 10, "status": "All"},
        {"totalCount": count_all_orders_from_db, "totalPages": 3, "pageIndex": 2, "hasPreviousPage": True, "hasNextPage": False}
    ),
    # 4. Some middle page with limit=1
    (
        {"page": 10, "limit": 1, "status": "All"},
        {"totalCount": count_all_orders_from_db, "totalPages": 21, "pageIndex": 10, "hasPreviousPage": True, "hasNextPage": True}
    ),
    # 5. Done orders in one page
    (
        {"page": 0, "limit": 40, "status": "Done"},
        {"totalCount": count_done_orders_from_db, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
    ),
    # 6. Cancel orders in one page
    (
        {"page": 0, "limit": 40, "status": "Cancel"},
        {"totalCount": count_cancel_orders_from_db, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
    )
]

# Generating good-looking names for reports
test_ids = [f"limit_{d[0]['limit']}_page_{d[0]['page']}_status_{d[0]['status']}" for d in test_data]

@pytest.mark.parametrize("inputs, expected", test_data, ids=test_ids)
def test_counts_and_navigation_parameters_positive_test_data(online_orders_api, inputs, expected):

    response = online_orders_api.get_online_orders(
        page=inputs["page"],
        limit=inputs["limit"],
        status=inputs["status"]
    )

    total_count = online_orders_api._get_json_value(response, "totalCount")
    page_index = online_orders_api._get_json_value(response, "pageIndex")
    total_pages = online_orders_api._get_json_value(response, "totalPages")
    has_previous_page = online_orders_api._get_json_value(response, "hasPreviousPage")
    has_next_page = online_orders_api._get_json_value(response, "hasNextPage")

    check.equal(total_count, expected["totalCount"], "Total count is wrong")
    check.equal(page_index, expected["pageIndex"], "Page index is wrong")
    check.equal(total_pages, expected["totalPages"], "Total pages is wrong")
    check.equal(has_previous_page, expected["hasPreviousPage"], "Has previous page is wrong")
    check.equal(has_next_page, expected["hasNextPage"], "Has next page is wrong")

def test_sum_done_and_cancel_orders(online_orders_api):

    response_all_orders = online_orders_api.get_online_orders(page=0, limit=40, status="All")
    total_count_all_orders = online_orders_api._get_json_value(response_all_orders, "totalCount")

    response_done_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Done")
    total_count_done_orders = online_orders_api._get_json_value(response_done_orders, "totalCount")

    response_cancel_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Cancel")
    total_count_cancel_orders = online_orders_api._get_json_value(response_cancel_orders, "totalCount")

    check.equal(count_all_orders_from_db,
                count_done_orders_from_db + count_cancel_orders_from_db,
                "Some of the count from db is wrong")
    check.equal(total_count_all_orders,
                total_count_done_orders + total_count_cancel_orders,
                "Some of the count from response is wrong")

test_data_3 = [
    ({"status": "All"}),
    ({"status": "Done"}),
    ({"status": "Cancel"})
]

# Generating good-looking names for reports
test_ids_3 = [f"limit=40_page=0_status_{d3['status']}" for d3 in test_data_3]

@pytest.mark.parametrize("inputs", test_data_3, ids=test_ids_3)
def test_scheme_orders_list(online_orders_api, inputs):
    response = online_orders_api.get_online_orders(page=0, limit=40, status=inputs["status"])
    OrdersResponse(**response.json())

test_data_2 = [
    ({"page": 0, "limit": 40, "status": "All"}),
    # ({"page": 0, "limit": 10, "status": "All"}),
    # ({"page": 1, "limit": 10, "status": "All"}),
    # ({"page": 2, "limit": 10, "status": "All"}),
    ({"page": 0, "limit": 40, "status": "Done"}),
    ({"page": 0, "limit": 40, "status": "Cancel"})
]

# Generating good-looking names for reports
test_ids_2 = [f"limit_{d2['limit']}_page_{d2['page']}_status_{d2['status']}" for d2 in test_data_2]

@pytest.mark.parametrize("inputs", test_data_2, ids=test_ids_2)
def test_quantity_items_for_different_status(online_orders_api, inputs):
    response = online_orders_api.get_online_orders(
        page=inputs["page"],
        limit=inputs["limit"],
        status=inputs["status"]
    )
    parsed_data = OrdersResponse(**response.json())

    check.equal(len(parsed_data.items), parsed_data.totalCount,
                "The number of items is not equal totalCount from response")


def test_quantity_items_for_pagination(online_orders_api):
    all_items = []
    for page in [0,1,2]:
        response = online_orders_api.get_online_orders(page=page, limit=10, status="All")
        parsed_data = OrdersResponse(**response.json())
        all_items.extend(parsed_data.items)

    check.equal(len(all_items), count_all_orders_from_db,
                "The number of items is not equal the quantity from db")
