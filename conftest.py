import pytest
import requests
from requests import Session
from common import config
from src.api.online_orders import OnlineOrdersAPI


@pytest.fixture(scope="session")
def api_session():
    session = Session()
    session.headers.update({
        "x-api-key": config.X_API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    })

    login_data = {"email": config.USER_PHONE_NUMBER, "password": config.USER_PASSWORD}
    login_res = session.post(f"{config.BASE_URL}/api/v2/auth/basic", json=login_data)

    access_token = login_res.json().get("accessToken")
    refresh_token = login_res.json().get("refreshToken")
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    info_res = session.get(f"{config.BASE_URL}/api/v2/auth/info/site-user")
    user_info = info_res.json()
    session.headers.update({"x-fuser-id": str(user_info["fUserId"])})
    #Adding this api_session_id attribute to session
    session.api_session_id = user_info["sessionId"]

    return session

@pytest.fixture
def online_orders_api(api_session):
    return OnlineOrdersAPI(base_url=config.BASE_URL, session=api_session)