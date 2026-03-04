import pytest
from requests import Session
from common import config
from src.api.online_orders import OnlineOrdersAPI
from common.logger import get_logger

logger = get_logger("FixtureSetup")

@pytest.fixture(scope="session")
def api_session():
    session = Session()
    session.headers.update({
        "x-api-key": config.X_API_KEY,
        "Content-Type": "application/json; charset=utf-8",
        "platform": config.PLATFORM,
        "mobile-version": config.MOBILE_VERSION,
    })

    login_data = {"login": config.USER_PHONE_NUMBER, "password": config.USER_PASSWORD}
    login_res = session.post(f"{config.BASE_URL}{config.API_VERSION}/auth/basic", json=login_data)
    if login_res.status_code != 200:
        logger.error(f"Login failed! Status: {login_res.status_code}, Response: {login_res.text}")
        login_res.raise_for_status()

    access_token = login_res.json().get("accessToken")
    refresh_token = login_res.json().get("refreshToken")
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    info_res = session.get(f"{config.BASE_URL}{config.API_VERSION}/auth/info/site-user")

    if info_res.status_code != 200:
        logger.error(f"Failed to get user info! Status: {info_res.status_code}, Response: {info_res.text}")
        info_res.raise_for_status()

    user_info = info_res.json()
    session.headers.update({"x-fuser-id": str(user_info["fUserId"])})
    #Adding this api_session_id attribute to session
    session.api_session_id = user_info["sessionId"]

    logger.info("Successfully authenticated and session initialized.")

    return session

@pytest.fixture
def online_orders_api(api_session):
    return OnlineOrdersAPI(base_url=config.BASE_URL, session=api_session)