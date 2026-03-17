import pytest
import pytest_check as check
from src.common.online_orders_data import Data
from src.models.orders.online_orders import OrdersResponse

class BaseOnlineOrders:
    def _get_orders(self, api, page=None, limit=None, status=None):
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

