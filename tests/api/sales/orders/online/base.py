import pytest
import pytest_check as check
from src.common.online_orders_data import Data
from src.models.orders.online_orders import OrdersResponse

class BaseOnlineOrders:
    def _get_orders(self, api, page=0, limit=40, status="All"):
        response = api.get_online_orders(page=page, limit=limit, status=status)
        return OrdersResponse(**response.json())

    def _get_items_from_pages(self, api, max_pages=5, **kwargs):
        page = 0
        total_pages = 1

        while page < total_pages and page < max_pages:
            data = self._get_orders(api, page=page, **kwargs)

            for item in data.items:
                yield item, page

            total_pages = data.totalPages
            page += 1

    def _check_each_image(self, items, page_num):
        for item in items:
            for url in item.goods:
                check.is_true(
                    url.startswith(Data.URL_PREFIX),
                    f"Page {page_num}: Item ID {item.id} has invalid image prefix!\n"
                    f"URL: {url}\n"
                    f"Expected prefix: {Data.URL_PREFIX}"
                )
                check.is_true(
                    url.lower().endswith(Data.ALLOWED_URL_SUFFIXES),
                    f"Page {page_num}: Item ID {item.id} has invalid extension. "
                    f"URL: {url}. Expected one of: {Data.ALLOWED_URL_SUFFIXES}"
                )