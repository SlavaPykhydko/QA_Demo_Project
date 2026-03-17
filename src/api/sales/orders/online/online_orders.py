from src.api.base_client import BaseClient

class OnlineOrdersAPI(BaseClient):
    def __init__(self, session):
        super().__init__(session=session)
        self.endpoint = "/sales/orders/online"

    # def get_online_orders(self, page=0, limit=40, status="All", raise_for_status=True):
    #
    #     query_params = {
    #         "Page": page,
    #         "Limit": limit,
    #         "Status": status
    #     }
    #
    #     return self._get(self.endpoint, params=query_params, raise_for_status=raise_for_status)


    def get_online_orders(self, page=None, limit=None, status=None, raise_for_status=True):
        query_params = {}

        if page is not None:
            query_params["Page"] = page
        if limit is not None:
            query_params["Limit"] = limit
        if status is not None:
            query_params["Status"] = status

        return self._get(self.endpoint, params=query_params, raise_for_status=raise_for_status)