import pytest
import pytest_check as check
import requests

from src.models.orders.online_orders import OrdersResponse, OrderItem
from src.common.online_orders_data import Data
from .base import BaseOnlineOrders
from concurrent.futures import ThreadPoolExecutor

class TestOnlineOrdersScheme(BaseOnlineOrders):
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page=0_status_{d['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_scheme(self, online_orders_api, inputs):
        parsed_data = self._get_orders(
            online_orders_api,
            page=0,
            limit=40,
            status=inputs["status"])

        assert len(parsed_data.items) >= 1
        assert parsed_data.totalPages > 0

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

class TestOnlineOrdersType(BaseOnlineOrders):
    def test_items_type(self, online_orders_api):
        expected_types = ["online", "marketplace"]

        for item, page in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
            check.is_in(item.type.lower(),
                        expected_types,
                        f"Page {page}: Item ID {item.id} has wrong type '{item.type} Expected one of: {expected_types}")


class TestOnlineOrdersFilterStatus(BaseOnlineOrders):
    test_data = [
        ({"status": "All"}),
        ({"status": "Done"}),
        ({"status": "Cancel"})
    ]

    # Generating good-looking names for reports
    test_ids = [f"limit=40_page_=0_status_{d['status']}" for d in test_data]

    @pytest.mark.parametrize("inputs", test_data, ids=test_ids)
    def test_quantity_items_for_each_status(self, online_orders_api, inputs):
        data = self._get_orders(
            online_orders_api,
            page=0,
            limit=40,
            status=inputs["status"])

        check.equal(len(data.items), data.totalCount,
                    "The number of items is not equal totalCount from response")


    # Creating mapping: what status is requested -> the list available statuses in the response
    status_mapping = [
        ("All", ["received", "canceled"]),  # For All are allowed both
        ("Done", ["received"]),
        ("Cancel", ["canceled"]),
    ]

    @pytest.mark.parametrize("requested_status, allowed_statuses", status_mapping)
    def test_each_item_has_correct_status(self, online_orders_api, requested_status, allowed_statuses):
        status_ua = ["отримано", "скасовано"]

        for item, page in self._get_items_from_pages(online_orders_api, limit=10, status=requested_status):
            check.is_in(
                item.orderStatus.lower(), allowed_statuses,
                f"Page {page}: Item ID {item.id} has wrong status '{item.orderStatus}'. "
                f"Expected one of: {allowed_statuses}"
            )
            check.is_in(
                item.statusGroup.lower(), allowed_statuses,
                f"Page {page}: Item ID {item.id} has wrong status '{item.statusGroup}'. "
                f"Expected one of: {allowed_statuses}"
            )
            check.is_in(
                item.status.lower(), status_ua,
                f"Page {page}: Item ID {item.id} has wrong status '{item.status}'. "
                f"Expected one of: {status_ua}"
            )


class TestOnlineOrdersPagination(BaseOnlineOrders):
    def test_sum_qnt_items_from_all_pages(self, online_orders_api, db_orders_counts):
        all_items = [item for item, page in self._get_items_from_pages(
            online_orders_api,
            limit=10,
            status="All")]

        check.equal(len(all_items), db_orders_counts["all"],
                    "The number of items is not equal the quantity from db")

class TestOnlineOrdersSellerConsistency(BaseOnlineOrders):
    def test_seller_and_type_consistency(self, online_orders_api):
        expected_types = ["online", "marketplace"]

        for item, page in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
            if item.seller.lower() == "епіцентр к":
                (check.equal(item.type.lower(), expected_types[0]),
                 f"For page='{page}' item type '{item.type}'or seller '{item.seller}' is wrong")
            else:
                (check.equal(item.type.lower(), expected_types[1]),
                 f"For page='{page}' item type  '{item.type}'or seller '{item.seller}' is wrong")


class TestOnlineOrdersIdsUniqueness(BaseOnlineOrders):
    def test_ids_uniqueness_across_all_pages(self, online_orders_api):
        all_collected_ids = []

        for item, page in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
            # Adding ID from the current page to common list
            all_collected_ids.append(item.id)

        # Final check for uniqueness all gathered ID
        duplicates = set([x for x in all_collected_ids if all_collected_ids.count(x) > 1])

        assert len(all_collected_ids) == len(set(all_collected_ids)), \
            f"Pagination bug! These IDs appear on multiple pages: {duplicates}"

class TestOnlineOrdersDateSorting(BaseOnlineOrders):
    def test_date_sorting(self, online_orders_api):
        actual_dates = []

        for item, page in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
            actual_dates.append([item.createdOn])

        # from new item to old one
        expected_dates = sorted(actual_dates, reverse=True)

        check.equal(
            actual_dates,
            expected_dates,
            "Orders are not sorted by date (newest first)!"
        )

class TestOnlineOrdersImage(BaseOnlineOrders):
    def test_each_image_parallel(self, online_orders_api):
        # # The 'with' construct will wait for all threads to complete before exiting.
        with ThreadPoolExecutor(max_workers=10) as executor:
            for item, page in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
                for url in item.goods:
                    if not url.startswith(Data.URL_PREFIX):
                        check.is_true(
                            False,
                            f"Page {page}: Item ID {item.id} has invalid image prefix!\n"
                            f"URL: {url}\n"
                            f"Expected prefix: {Data.URL_PREFIX}")
                        continue
                    if not url.lower().endswith(Data.ALLOWED_URL_SUFFIXES):
                        check.is_true(
                            False,
                            f"Page {page}: Item ID {item.id} has invalid extension. "
                            f"URL: {url}. Expected one of: {Data.ALLOWED_URL_SUFFIXES}")
                        continue
                    # We send a heavy network check to the thread
                    executor.submit(self._check_single_url, url, item.id, page)

    def _check_single_url(self, url, item_id, page):
        """ Function-worker for 1 thread """
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            check.equal(
                response.status_code, 200,
                f"Page {page}: ID {item_id} - URL {url} returned {response.status_code}"
            )
        except Exception as e:
            check.is_true(False, f"Page {page}: Item ID {item_id} URL unreachable: {url}. Error: {e}")

class TestOnlineOrdersPrice(BaseOnlineOrders):
    def test_order_prices(self, online_orders_api):
        for item, page  in self._get_items_from_pages(online_orders_api, limit=10, status="All"):
            check.greater(item.price, 0, f"Item {item.id} has invalid price: {item.price}")


class TestOnlineOrdersGoodsQuantity(BaseOnlineOrders):
    def test_order_goods_quantity(self, online_orders_api):
        page = 0
        total_pages = 1
        while page < total_pages:
            data = self._get_orders(online_orders_api, page=page, limit=10, status="All")
            total_pages = data.totalPages
            for item in data.items:
                check.greater(item.quantity, 0, f"Item {item.id} has invalid quantity: {item.quantity}")
            page += 1

class TestOnlineOrdersGoodsAndImageConsistency(BaseOnlineOrders):
    def test_goods_qnt_equal_image_qnt(self, online_orders_api):
        page = 0
        total_pages = 1

        while page < total_pages:
            data = self._get_orders(online_orders_api, page=page, limit=10, status="All")
            total_pages = data.totalPages

            for item in data.items:
                check.equal(
                    len(item.goods),
                    item.quantity,
                    f"Item {item.id} has invalid qnt: {item.quantity} or invalid qnt of pictures: {item.goods}"
                )
            page += 1

class TestOnlineOrdersIdAndNameConsistency(BaseOnlineOrders):
    def test_id_and_name_consistency(self, online_orders_api):
        page = 0
        total_pages = 1

        while page < total_pages:
            data = self._get_orders(online_orders_api, page=page, limit=10, status="Cancel")
            total_pages = data.totalPages

            for item in data.items:
                check.equal(str(item.id), item.name, f"Item {item.id} has invalid name: {item.name}")
            page += 1

class TestOnlineOrdersOrderDataEqualDataFromDB(BaseOnlineOrders):
    def test_order_data_equal_data_from_db(self, online_orders_api, db_online_orders_map):
        for api_item, page in self._get_items_from_pages(
                online_orders_api,
                limit=10,
                status="Cancel"):

            db_item = db_online_orders_map[api_item.id]
            # Checking whether the order is in the DB
            if check.is_not_none(db_item, f"Order {api_item.id} found in API but missing in DB!"):
                # Compare each value except EXCLUDE_FIELDS
                self._compare_items(api_item, db_item, page)


    def _compare_items(self, api_item, db_item, page_num):
        EXCLUDE_FIELDS = {"createdOn", "goods"}

        # .model_dump() transforms Pydantic-object to usual dict
        api_dict = api_item.model_dump()
        db_dict = db_item.model_dump()

        for key in api_dict.keys():
            if key in EXCLUDE_FIELDS:
                continue

            api_val = api_dict[key]
            db_val = db_dict[key]

            check.equal(
                api_val,
                db_val,
                f"Page {page_num}: Order ID {api_item.id} -> Mismatch in field '{key}'!\n"
                f"API: {api_val}\n"
                f"DB:  {db_val}"
            )
