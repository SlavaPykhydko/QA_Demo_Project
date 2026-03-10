from src.database.db_client import db_client


class OnlineOrdersData:

    @property
    def ALL(self):
        return db_client.get_online_orders_counts()["all"]
    @property
    def DONE(self):
        return db_client.get_online_orders_counts()["done"]
    @property
    def CANCEL(self):
        return db_client.get_online_orders_counts()["cancel"]

    URL_PREFIX = "https://cdn.27.ua/"
    ALLOWED_URL_SUFFIXES = (".jpg", ".jpeg")

Data = OnlineOrdersData()