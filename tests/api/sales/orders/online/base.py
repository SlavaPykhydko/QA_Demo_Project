from src.models.orders.online_orders import OrdersResponse

class BaseOnlineOrders:
    def _get_orders(self, api, page=0, limit=40, status="All"):
        response = api.get_online_orders(page=page, limit=limit, status=status)
        return OrdersResponse(**response.json())