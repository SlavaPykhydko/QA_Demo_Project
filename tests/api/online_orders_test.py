import pytest
import pytest_check as check

# Defining test data (input parameters, expected results)
test_data = [
    # 1. All orders in one page
    (
        {"page": 0, "limit": 40, "status": "All"},
        {"totalCount": 21, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
    ),
    # 2. The first page with limit=10
    (
        {"page": 0, "limit": 10, "status": "All"},
        {"totalCount": 21, "totalPages": 3, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": True}
    ),
    # 3. The last page with limit=10
    (
        {"page": 2, "limit": 10, "status": "All"},
        {"totalCount": 21, "totalPages": 3, "pageIndex": 2, "hasPreviousPage": True, "hasNextPage": False}
    ),
    # 4. Some middle page with limit=1
    (
        {"page": 10, "limit": 1, "status": "All"},
        {"totalCount": 21, "totalPages": 21, "pageIndex": 10, "hasPreviousPage": True, "hasNextPage": True}
    ),
    # 5. Done orders in one page
    (
        {"page": 0, "limit": 40, "status": "Done"},
        {"totalCount": 19, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
    ),
    # 6. Cancel orders in one page
    (
        {"page": 0, "limit": 40, "status": "Cancel"},
        {"totalCount": 2, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
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
