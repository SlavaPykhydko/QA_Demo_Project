from src.api.base_client import BaseClient

class OnlineOrdersAPI(BaseClient):
    def __init__(self, session):
        super().__init__(session=session)
        self.endpoint = "/sales/orders/online"

    def get_online_orders(self, page=0, limit=40, status="All"):

        query_params = {
            "Page": page,
            "Limit": limit,
            "Status": status
        }

        return self._get(self.endpoint, params=query_params)