import pytest
import pytest_check as check

def test_check_orders_list(online_orders_api):


    response = online_orders_api.get_online_orders(page=0, limit=40, status="ALL")
    expected_total_count = 21
    expected_page_index = 0
    expected_total_pages = 1
    expected_has_previous_page = False
    expected_has_next_page = False


    total_count = online_orders_api._get_json_value(response, "totalCount")
    page_index = online_orders_api._get_json_value(response, "pageIndex")
    total_pages = online_orders_api._get_json_value(response, "totalPages")
    has_previous_page = online_orders_api._get_json_value(response, "hasPreviousPage")
    has_next_page = online_orders_api._get_json_value(response, "hasNextPage")

    check.equal(total_count, expected_total_count, "Total count is wrong")
    check.equal(page_index, expected_page_index, "Page index is wrong")
    check.equal(total_pages, expected_total_pages, "Total pages is wrong")
    check.equal(has_previous_page, expected_has_previous_page, "Has previous page is wrong")
    check.equal(has_next_page, expected_has_next_page, "Has next page is wrong")
