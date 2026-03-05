import pytest
from requests import Session
from common import config
from src.api.online_orders import OnlineOrdersAPI
from common.logger import get_logger

# Creating logger for fixture/reports
report_logger = get_logger("TestReport")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Running test
    outcome = yield
    report = outcome.get_result()

    # If test failed at the beginning
    if report.when == "call" and report.failed:
        # Logging test's name and error (including errors which pytest-check found)
        report_logger.error(f" TEST FAILED: {item.nodeid} ")

        # Adding error text (longrepr - it's what we see in the console)
        if report.longrepr:
            # Transformation error's object into text and log into file
            report_logger.error(f"FAILURE DETAILS:\n{report.longreprtext}")

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
        report_logger.error(f"Login failed! Status: {login_res.status_code}, Response: {login_res.text}")
        login_res.raise_for_status()

    access_token = login_res.json().get("accessToken")
    refresh_token = login_res.json().get("refreshToken")
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    info_res = session.get(f"{config.BASE_URL}{config.API_VERSION}/auth/info/site-user")

    if info_res.status_code != 200:
        report_logger.error(f"Failed to get user info! Status: {info_res.status_code}, Response: {info_res.text}")
        info_res.raise_for_status()

    user_info = info_res.json()
    session.headers.update({"x-fuser-id": str(user_info["fUserId"])})
    #Adding this api_session_id attribute to session
    session.api_session_id = user_info["sessionId"]

    report_logger.info("Successfully authenticated and session initialized.")

    return session

@pytest.fixture
def online_orders_api(api_session):
    return OnlineOrdersAPI(base_url=config.BASE_URL, session=api_session)