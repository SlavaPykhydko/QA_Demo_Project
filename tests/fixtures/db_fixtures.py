import pytest

from src.database.db_client import FakeDBClient
from src.models.orders.online_orders import OrderItem


@pytest.fixture(scope="session")
def db(cfg):
    # Unless we have access to real DB, use Fake DB client
    # Later this can be switched to DBClient(cfg)
    db_client = FakeDBClient()
    return db_client


@pytest.fixture(scope="session")
def db_orders_counts(db):
    return db.get_online_orders_counts()


@pytest.fixture(scope="session")
def db_online_orders_map(db):
    # 1. Getting raw data (list[dict])
    raw_data = db.get_online_orders_from_history_table()

    # 2. Transform to quick lookup map: {id: OrderItem}
    return {item["id"]: OrderItem(**item) for item in raw_data}


