import pytest
from requests import Session
from src.common.config import config

from src.common.logger import get_logger
from src.api.sales.orders.online.online_orders import OnlineOrdersAPI
from src.database.db_client import db_client
from src.models.orders.online_orders import OrderItem

# Creating logger for fixture/reports
report_logger = get_logger("TestReport")

@pytest.fixture(scope="session")
def db_orders_counts():
    counts = db_client.get_online_orders_counts()
    return counts

@pytest.fixture(scope="session")
def db_online_orders_map():
    # 1. Getting raw data (list dicts)
    raw_data = db_client.get_online_orders_from_history_table()

    # 2. Transform them into map OrderItem's object
    # Now it's not just a list it's a quick reference book{id: object}
    orders_map = {item['id']: OrderItem(**item) for item in raw_data}

    return orders_map

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Running test
    outcome = yield
    report = outcome.get_result()

    # If test failed at the beginning
    if report.when == "call" and report.failed:
        # 1. Getting tests params (if there is a parametrization)
        params = item.callspec.params if hasattr(item, 'callspec') else "No params"

        # 2. Forming a good-looking frame for errors
        error_separator = "!" * 80
        report_logger.error(f"\n{error_separator}")
        report_logger.error(f"TEST FAILED: {item.nodeid}")
        report_logger.error(f"PARAMS: {params}")

        # Adding error text (longrepr - it's what we see in the console)
        if report.longrepr:
            # 3. We get only the most important from the error (reprcrash)
            # or all text if it's a soft checks (pytest-check)
            error_details = report.longreprtext

            # If the log is too long, we can leave only the last N strings
            # where usually there is an error pytest-check
            report_logger.error(f"FAILURE REASON:\n{error_details}")

        report_logger.error(f"{error_separator}\n")

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
    return OnlineOrdersAPI(session=api_session)