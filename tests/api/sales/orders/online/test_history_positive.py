import allure
import pytest
import pytest_check as check
import requests
from concurrent.futures import ThreadPoolExecutor
from data.online_orders_constants import ALLOWED_IMAGE_EXTENSIONS, LIMIT_40
from src.common.enums.orders import StatusUA, Status, OrderType

from data.online_orders_positive_data import (
    LIST_INFO_DATA,
    ORDER_STATUS_MAPPING,
    STATUS_DATA,
    STATUS_GROUP_MAPPING,
)


# Now ALL tests in this file are automatically labeled 'positive' and 'regression'
pytestmark = [
    pytest.mark.positive,
    pytest.mark.regression,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Positive checks")
]

class TestScheme:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Check contract with status: {inputs[status]}")  # Dynamic title
    @pytest.mark.parametrize("inputs", STATUS_DATA)
    def test_scheme(self, api, inputs):
        parsed_data = api.online_orders.get_parsed_items(
            page=0,
            limit=LIMIT_40,
            status=inputs["status"])

        with allure.step(f"Check items lengths more or equal 1 "):
            check.greater_equal( len(parsed_data.items), 1, "List of items must be >= 1")
        with allure.step(f"Check totalPages more 0 "):
            check.greater(parsed_data.totalPages, 0, "totalPages param must be > 0")

class TestListInfo:

    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check list info params with inputs: {inputs}")
    @pytest.mark.parametrize("inputs, expected", LIST_INFO_DATA)
    def test_list_info_params(self, api, inputs, expected, db_orders_counts):
        expected_total_count = db_orders_counts[expected["totalCount"]]

        response = api.online_orders.get_items(
            page=inputs["page"],
            limit=inputs["limit"],
            status=inputs["status"]
        )

        total_count = api.online_orders._get_json_value(response, "totalCount")
        page_index = api.online_orders._get_json_value(response, "pageIndex")
        total_pages = api.online_orders._get_json_value(response, "totalPages")
        has_previous_page = api.online_orders._get_json_value(response, "hasPreviousPage")
        has_next_page = api.online_orders._get_json_value(response, "hasNextPage")

        with allure.step(f"Check totalCount"):
            check.equal(total_count, expected_total_count, "Total count is wrong")
        with allure.step(f"Check pageIndex"):
            check.equal(page_index, expected["pageIndex"], "Page index is wrong")
        with allure.step(f"Check totalPages"):
            check.equal(total_pages, expected["totalPages"], "Total pages is wrong")
        with allure.step(f"Check hasPreviousPage"):
            check.equal(has_previous_page, expected["hasPreviousPage"], "Has previous page is wrong")
        with allure.step(f"Check hasNextPage"):
            check.equal(has_next_page, expected["hasNextPage"], "Has next page is wrong")


    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check sum of Done and Canceled orders:")
    def test_sum_done_cancel_active_orders(self, api, db_orders_counts):
        res_all_orders = api.online_orders.get_items(page=0, limit=LIMIT_40, status=Status.ALL)
        total_count_all_orders = api.online_orders._get_json_value(res_all_orders, "totalCount")

        res_done_orders = api.online_orders.get_items(page=0, limit=LIMIT_40, status=Status.DONE)
        total_count_done_orders = api.online_orders._get_json_value(res_done_orders, "totalCount")

        res_cancel_orders = api.online_orders.get_items(page=0, limit=LIMIT_40, status=Status.CANCEL)
        total_count_cancel_orders = api.online_orders._get_json_value(res_cancel_orders, "totalCount")

        res_cancel_orders = api.online_orders.get_items(page=0, limit=LIMIT_40, status=Status.ACTIVE)
        total_count_active_orders = api.online_orders._get_json_value(res_cancel_orders, "totalCount")

        with allure.step(f"Check from DB all = done + cancel"):
            check.equal(db_orders_counts["all"],
                        db_orders_counts["done"] + db_orders_counts["cancel"] + db_orders_counts["active"],
                        "Some of the count from db is wrong")
        with allure.step(f"Check from response all = done + cancel"):
            check.equal(total_count_all_orders,
                        total_count_done_orders + total_count_cancel_orders + total_count_active_orders,
                        "Some of the count from response is wrong")



class TestItemType:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Item type belongs to one of the expected_types")
    def test_item_type(self, api):
        expected_types = [t.value for t in OrderType]

        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"For tem ID: {item.id} check each item type is one of the expected_types {expected_types}"):
                check.is_in(
                    item.type,
                    expected_types,
                     f"Page {page}: Item ID {item.id} has wrong type {item.type} Expected one of: {expected_types}")


class TestOnlineOrdersFilterStatus:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check quantity items with status: {inputs[status]}")
    @pytest.mark.parametrize("inputs", STATUS_DATA)
    def test_quantity_items_for_each_status(self, api, inputs):
        data = api.online_orders.get_parsed_items(
            page=0,
            limit=LIMIT_40,
            status=inputs["status"])
        with allure.step(f"Check len items from response equal totalCount param"):
            check.equal(len(data.items), data.totalCount,
                        "The number of items is not equal totalCount from response")



    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check each item from items has correct orderStatus and status params with input status: {requested_status}")
    @pytest.mark.parametrize("requested_status, allowed_statuses", ORDER_STATUS_MAPPING)
    def test_each_item_has_correct_status(self, api, requested_status, allowed_statuses):
        allowed_statuses_ua = [s.value for s in StatusUA]

        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=requested_status):
            with allure.step(f"For item ID: {item.id} check item.orderStatus is one of the {allowed_statuses}"):
                check.is_in(
                    item.orderStatus, allowed_statuses,
                    f"Page {page}: Item ID {item.id} has wrong status '{item.orderStatus}'. "
                    f"Expected one of: {allowed_statuses}"
                )
            with allure.step(f"For item ID: {item.id} check item.status in UA lang on of the {allowed_statuses_ua}"):
                check.is_in(
                    item.status, item.orderStatus.ukrainian.value,
                    f"Page {page}: Item ID {item.id} has wrong status '{item.status}'. "
                    f"Expected one of: {allowed_statuses_ua}"
                )


    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check each item from items has correct statusGroup param with input status: {requested_status}")
    @pytest.mark.parametrize("requested_status, allowed_statuses", STATUS_GROUP_MAPPING)
    def test_each_item_has_correct_status_group(self, api, requested_status, allowed_statuses):
        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=requested_status):
            with allure.step(f"For item ID: {item.id} check item.statusGroup is one of the {allowed_statuses}"):
                check.is_in(
                    item.statusGroup.lower(), allowed_statuses,
                    f"Page {page}: Item ID {item.id} has wrong status '{item.statusGroup}'. "
                    f"Expected one of: {allowed_statuses}"
                )


class TestQntAllItemsViaPagination:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check sum qnt items from all pages")
    def test_sum_qnt_items_from_all_pages(self, api, db_orders_counts):
        all_items = [item for item, page in api.online_orders.get_items_with_pagination(
            limit=LIMIT_40,
            status=Status.ALL)]
        with allure.step(f"Check len all items from all pages in response equal all items from DB"):
            check.equal(len(all_items), db_orders_counts["all"],
                        "The number of items is not equal the quantity from db")

class TestSellerConsistency:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Check consistency seller with selling type")
    def test_seller_and_selling_type_consistency(self, api):
        expected_types = [t.value for t in OrderType]

        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"For item ID {item.id} check item.type is one of the {expected_types}"):
                if item.seller.lower() == "епіцентр к":
                    (check.equal(item.type, OrderType.ONLINE),
                     f"For page='{page}' item type '{item.type}'or seller '{item.seller}' is wrong")
                else:
                    (check.equal(item.type, OrderType.MARKETPLACE),
                     f"For page='{page}' item type  '{item.type}'or seller '{item.seller}' is wrong")


class TestIdsUniqueness:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("All ids are unique")
    def test_ids_uniqueness(self, api):
        all_collected_ids = []

        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            # Adding ID from the current page to common list
            all_collected_ids.append(item.id)
            # Final check for uniqueness all gathered ID
            duplicates = set([x for x in all_collected_ids if all_collected_ids.count(x) > 1])

        with allure.step(f"Check ids are unique"):
            assert len(all_collected_ids) == len(set(all_collected_ids)), \
                f"Pagination bug! These IDs appear on multiple pages: {duplicates}"

class TestOrdersSorting:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("All items sorted by date")
    def test_item_sorting_by_date(self, api):
        actual_dates = []

        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            actual_dates.append([item.createdOn])

        # from new item to old one
        expected_dates = sorted(actual_dates, reverse=True)

        with allure.step(f"Check all items from response sorted by date. Newest first"):
            check.equal(
                actual_dates,
                expected_dates,
                "Orders are not sorted by date (newest first)!"
            )

class TestOnlineOrdersImage:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Each picture from orders isn't broken")
    def test_image_is_not_broken(self, api, cfg):
        # # The 'with' construct will wait for all threads to complete before exiting.
        with ThreadPoolExecutor(max_workers=10) as executor:
            for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
                for url in item.goods:
                    with allure.step(f"For item ID {item.id} verify prefix and extension for: {url}"):
                        if not url.startswith(cfg.URL_PREFIX):
                            check.is_true(
                                False,
                                f"Page {page}: Item ID {item.id} has invalid image prefix!\n"
                                f"URL: {url}\n"
                                f"Expected prefix: {cfg.URL_PREFIX}")
                            continue
                        if not url.lower().endswith(ALLOWED_IMAGE_EXTENSIONS):
                            check.is_true(
                                False,
                                f"Page {page}: Item ID {item.id} has invalid extension. "
                                f"URL: {url}. Expected one of: {ALLOWED_IMAGE_EXTENSIONS}")
                            continue
                    # We send a heavy network check to the thread
                    executor.submit(self._check_single_url, url, item.id, page)

    def _check_single_url(self, url, item_id, page):
        with allure.step(f"For item ID {item_id} check status code for each image with {url}"):
            """ Function-worker for 1 thread """
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                check.equal(
                    response.status_code, 200,
                    f"Page {page}: ID {item_id} - URL {url} returned {response.status_code}"
                )
            except Exception as e:
                check.is_true(False, f"Page {page}: Item ID {item_id} URL unreachable: {url}. Error: {e}")

class TestOrderPrice:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Each order price more than 0")
    def test_item_price_param(self, api):
        for item, page  in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"For item ID: {item.id} check item.price more than 0"):
                check.greater(item.price, 0, f"Item {item.id} has invalid price: {item.price}")


class TestQuantityParam:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Quantity param in each item more than 0")
    def test_item_qnt_param(self, api):
        for item, page  in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"For item ID: {item.id} check item.quantity more than 0"):
                check.greater(item.quantity, 0, f"Item {item.id} has invalid quantity: {item.quantity}")


class TestGoodsAndImageConsistency:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Qnt param in each item equal qnt images")
    def test_item_qnt_param_equal_image_qnt(self, api):
        for item, page  in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"For item ID: {item.id} check item.quantity param equal qnt images"):
                check.equal(
                    len(item.goods),
                    item.quantity,
                    f"Item {item.id} has invalid qnt: {item.quantity} or invalid qnt of pictures: {item.goods}")


class TestIdAndNameConsistency:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Item name and id are similar")
    def test_id_and_name_consistency(self, api):
        for item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.ALL):
            with allure.step(f"Check consistency for item ID: {item.id}"):
                check.equal(str(item.id), item.name, f"Item {item.id} has invalid name: {item.name}")


class TestOrderDataEqualDataFromDB:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Item Data from Response equal data from DB")
    def test_order_data_equal_data_from_db(self, api, db_online_orders_map):
        for api_item, page in api.online_orders.get_items_with_pagination(limit=LIMIT_40, status=Status.CANCEL):
            db_item = db_online_orders_map[api_item.id]
            with allure.step(f"Checking whether the order with ID: {api_item.id}  is in the DB"):
                if check.is_not_none(db_item, f"Order {api_item.id} found in API but missing in DB!"):
                    with allure.step("Compare each value except EXCLUDE_FIELDS"):
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

            check.equal(api_val, db_val,
                f"Page {page_num}: Order ID {api_item.id} -> Mismatch in field '{key}'!\n"
                f"API: {api_val}\n"
                f"DB:  {db_val}"
            )

class TestDefaultsParams:

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify default 'Status' behavior (should default to 'All')")
    def test_default_status_is_all(self, api, db_orders_counts):
        expected_count_all = db_orders_counts["all"]
        parsed_data = api.online_orders.get_parsed_items(
            page=0,
            limit=LIMIT_40
        )

        with allure.step(f"Verify that items are returned (defaulting works)"):
            check.greater( len(parsed_data.items), 1, "Should return items even without explicit param Status")
        with allure.step(f"Verify that default param Status is status={Status.ALL})"):
            check.equal(parsed_data.totalCount, expected_count_all, f"Default param Status must be status={Status.ALL}")