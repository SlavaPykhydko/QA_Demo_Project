from src.api.base_client import BaseClient
from src.models.orders.online_orders import OrdersResponse


class OnlineOrdersAPI(BaseClient):
    def __init__(self, session):
        super().__init__(session=session)
        self.endpoint = "/sales/orders/online"

    def get_parsed_items(self, page=None, limit=None, status=None):
        response = self.get_items(page=page, limit=limit, status=status)
        return OrdersResponse(**response.json())

    def get_items_with_pagination(self, max_pages=5, **kwargs):
        page = 0
        total_pages = 1

        while page < total_pages and page < max_pages:
            data = self.get_parsed_items(page=page, **kwargs)

            for item in data.items:
                yield item, page

            total_pages = data.totalPages
            page += 1

    def get_items(self, page=None, limit=None, status=None, raise_for_status=True):
        query_params = {}

        if page is not None:
            query_params["Page"] = page
        if limit is not None:
            query_params["Limit"] = limit
        if status is not None:
            query_params["Status"] = status

        return self._get(self.endpoint, params=query_params, raise_for_status=raise_for_status)