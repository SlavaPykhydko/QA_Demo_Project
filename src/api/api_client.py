from requests import Session

from src.api.sales.orders.online.online_orders import OnlineOrdersAPI


class ApiClient:
    def __init__(self, config, session: Session):
        # Passing one and the same config to all services
        self.online_orders = OnlineOrdersAPI(session=session, config=config)