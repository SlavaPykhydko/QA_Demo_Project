class OnlineOrdersExpectedData:
    def __init__(self, db_client, config):
        self.db_client = db_client
        self.URL_PREFIX = config.URL_PREFIX
        self.ALLOWED_URL_EXTENSIONS = (".jpg", ".jpeg")

    @property
    def ALL(self):
        return self.db_client.get_online_orders_counts()["all"]

    @property
    def DONE(self):
        return self.db_client.get_online_orders_counts()["done"]

    @property
    def CANCEL(self):
        return self.db_client.get_online_orders_counts()["cancel"]

