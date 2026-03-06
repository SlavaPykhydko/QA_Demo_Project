import pytest_check as check
from tests.conftest import db_counts

def test_sum_done_and_cancel_orders(online_orders_api, db_counts):

    res_all_orders = online_orders_api.get_online_orders(page=0, limit=40, status="All")
    total_count_all_orders = online_orders_api._get_json_value(res_all_orders, "totalCount")

    res_done_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Done")
    total_count_done_orders = online_orders_api._get_json_value(res_done_orders, "totalCount")

    res_cancel_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Cancel")
    total_count_cancel_orders = online_orders_api._get_json_value(res_cancel_orders, "totalCount")

    check.equal(db_counts["all"],
                db_counts["done"] + db_counts["cancel"],
                "Some of the count from db is wrong")
    check.equal(total_count_all_orders,
                total_count_done_orders + total_count_cancel_orders,
                "Some of the count from response is wrong")



