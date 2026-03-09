import pytest
import pytest_check as check
from src.models.orders.online_orders import OrdersResponse
from src.common.online_orders_data import Data

class TestOnlineOrdersScheme:
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_scheme(self, online_orders_api, inputs):
        response = online_orders_api.get_online_orders(page=0, limit=40, status=inputs["status"])
        OrdersResponse(**response.json())

class TestOnlineOrdersListInfo:
    # Defining test data (input parameters, expected results)
    test_data = [
        # 1. All orders in one page
        (
            {"page": 0, "limit": 40, "status": "All"},
            {"totalCount": Data.ALL, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
        ),
        # 2. The first page with limit=10
        (
            {"page": 0, "limit": 10, "status": "All"},
            {"totalCount": Data.ALL, "totalPages": 3, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": True}
        ),
        # 3. The last page with limit=10
        (
            {"page": 2, "limit": 10, "status": "All"},
            {"totalCount": Data.ALL, "totalPages": 3, "pageIndex": 2, "hasPreviousPage": True, "hasNextPage": False}
        ),
        # 4. Some middle page with limit=1
        (
            {"page": 10, "limit": 1, "status": "All"},
            {"totalCount": Data.ALL, "totalPages": Data.ALL, "pageIndex": 10, "hasPreviousPage": True,
             "hasNextPage": True}
        ),
        # 5. Done orders in one page
        (
            {"page": 0, "limit": 40, "status": "Done"},
            {"totalCount": Data.DONE, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
        ),
        # 6. Cancel orders in one page
        (
            {"page": 0, "limit": 40, "status": "Cancel"},
            {"totalCount": Data.CANCEL, "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False}
        )
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit_{d[0]['limit']}_page_{d[0]['page']}_status_{d[0]['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs, expected", test_data, ids=test_ids)
    def test_list_info_params(self, online_orders_api, inputs, expected, db_orders_counts):
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

        # just for self-checking
        check.equal(Data.ALL, db_orders_counts["all"])
        check.equal(Data.CANCEL, db_orders_counts["cancel"])
        check.equal(Data.DONE, db_orders_counts["done"])

    def test_sum_done_and_cancel_orders(self, online_orders_api, db_orders_counts):
        res_all_orders = online_orders_api.get_online_orders(page=0, limit=40, status="All")
        total_count_all_orders = online_orders_api._get_json_value(res_all_orders, "totalCount")

        res_done_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Done")
        total_count_done_orders = online_orders_api._get_json_value(res_done_orders, "totalCount")

        res_cancel_orders = online_orders_api.get_online_orders(page=0, limit=40, status="Cancel")
        total_count_cancel_orders = online_orders_api._get_json_value(res_cancel_orders, "totalCount")

        check.equal(db_orders_counts["all"],
                    db_orders_counts["done"] + db_orders_counts["cancel"],
                    "Some of the count from db is wrong")
        check.equal(total_count_all_orders,
                    total_count_done_orders + total_count_cancel_orders,
                    "Some of the count from response is wrong")

class TestOnlineOrdersQntItemsForDiffStatus:
    test_data = [
        ({"page": 0, "limit": 40, "status": "All"}),
        ({"page": 0, "limit": 40, "status": "Done"}),
        ({"page": 0, "limit": 40, "status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit_{d['limit']}_page_{d['page']}_status_{d['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_quantity_items_for_different_status(self, online_orders_api, inputs):
        response = online_orders_api.get_online_orders(
            page=inputs["page"],
            limit=inputs["limit"],
            status=inputs["status"]
        )
        parsed_data = OrdersResponse(**response.json())

        check.equal(len(parsed_data.items), parsed_data.totalCount,
                    "The number of items is not equal totalCount from response")

class TestOnlineOrdersSumQntItemsForPagination:
    def test_sum_qnt_items_from_all_pages(self, online_orders_api, db_orders_counts):
        all_items = []
        for page in [0, 1, 2]:
            response = online_orders_api.get_online_orders(page=page, limit=10, status="All")
            parsed_data = OrdersResponse(**response.json())
            all_items.extend(parsed_data.items)

        check.equal(len(all_items), db_orders_counts["all"],
                    "The number of items is not equal the quantity from db")
