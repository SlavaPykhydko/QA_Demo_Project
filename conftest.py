import pytest
import requests
from common import config
from src.api.online_orders import OnlineOrdersAPI


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()

    login_data = {"email": config.USER_EMAIL, "password": config.USER_PASSWORD}
    response = session.post(f"{config.BASE_URL}/api/v1/auth/login", json=login_data)

    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})

    return session

@pytest.fixture
def online_orders_api(api_session):
    return OnlineOrdersAPI(base_url=config.BASE_URL, session=api_session)