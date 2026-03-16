import pytest
from requests import Session
from src.common.config import config

from src.common.logger import get_logger
from src.api.sales.orders.online.online_orders import OnlineOrdersAPI
from src.common.user_accounts import UserAccounts
from src.database.db_client import db_client
from src.models.orders.online_orders import OrderItem

# Creating logger for fixture/reports
report_logger = get_logger("TestReport")


# Generating good-looking names for reports
def pytest_make_parametrize_id(val, argname):
    if argname == "inputs" and isinstance(val, dict):
        # Выбираем важные ключи для названия
        items = list(val.items())[:3]
        return "-".join([f"{k}_{v}" for k, v in items])

    if argname in ["expected", "allowed_statuses"]:
        return ""

    return None

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

# --- Layer #1: Base session ---
@pytest.fixture(scope="session")
def base_session():
    """Creating a session 'foundation' with common headers"""
    session = Session()
    session.headers.update({
        "x-api-key": config.X_API_KEY,
        "Content-Type": "application/json; charset=utf-8",
        "platform": config.PLATFORM,
        "mobile-version": config.MOBILE_VERSION,
    })
    return session


# --- Layer #2 Smart authorization  ---
# Благодаря scope="module" выполнится один раз для каждого типа юзера в файле.
@pytest.fixture(scope="module")
def user_session(base_session, request):
    """
    Converts a basic session to an authorized session for a specific user.
    First, it checks whether a specific user was passed via parameters.
    If not, it takes the main user (USER_WITH_HISTORY) by default.
    """
    # 1. Выбираем юзера.
    # getattr ищет 'param' в объекте request. Если его нет — берет дефолт.
    user_data = getattr(request, "param", UserAccounts.USER_WITH_HISTORY)

    session = base_session

    report_logger.info(f"Attempting login for: {user_data.login}")

    login_payload = {
        "login": user_data.login,
        "password": user_data.password
    }

    login_res = session.post(f"{config.BASE_URL}{config.API_VERSION}/auth/basic", json=login_payload)
    if login_res.status_code != 200:
        report_logger.error(f"Login failed! Status: {login_res.status_code}, Response: {login_res.text}")
        login_res.raise_for_status()

    access_token = login_res.json().get("accessToken")
    refresh_token = login_res.json().get("refreshToken")

    # 3. Обновляем заголовки (Token + fUserId)
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

    yield session

    # 4. Teardown (Чистим сессию, чтобы следующий тест не "наследовал" этого юзера)
    session.headers.pop("Authorization", None)
    session.headers.pop("x-fuser-id", None)
    if hasattr(session, "api_session_id"):
        del session.api_session_id

# --- Layer #3 Specific endpoints  ---
@pytest.fixture(scope="module")
def online_orders_api(user_session):
    return OnlineOrdersAPI(session=user_session)