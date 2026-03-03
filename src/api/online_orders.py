from src.api.base_client import BaseClient

class OnlineOrdersAPI(BaseClient):
    def __init__(self, base_url, session):
        super().__init__(base_url, session)
        self.endpoint = "/api/v2/sales/orders/online"

    def get_online_orders(self, page=0, limit=40, status="All", session_id=None):

        query_params = {
            "Page": page,
            "Limit": limit,
            "Status": status,
            "session_id": session_id
        }

        return self._get(self.endpoint, params=query_params)