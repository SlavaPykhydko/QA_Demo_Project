import pytest
from requests import Session

from src.api.api_client import ApiClient
from src.common.logger import get_logger
from src.common.user_accounts import UserFactory, UserType


report_logger = get_logger("TestReport")


# --- Layer #1: Base session ---
@pytest.fixture(scope="session")
def base_session(cfg):
    """Create a shared session with common headers."""
    session = Session()
    session.headers.update(
        {
            "x-api-key": cfg.X_API_KEY,
            "Content-Type": "application/json; charset=utf-8",
            "platform": cfg.PLATFORM,
            "mobile-version": cfg.MOBILE_VERSION,
        }
    )
    return session


# --- Layer #2: Smart authorization ---
@pytest.fixture(scope="module")
def user_session(base_session, request, cfg):
    """Return an authorized session for a selected user type."""
    # getattr looks for 'param' in request; if absent, use default user
    user_type = getattr(request, "param", UserType.WITH_HISTORY)
    user = UserFactory.get_user(user_type, cfg)

    session = base_session
    report_logger.info(f"Attempting login for: {user.login}")

    login_payload = {"login": user.login, "password": user.password}
    login_res = session.post(f"{cfg.BASE_URL}{cfg.API_VERSION}/auth/basic", json=login_payload)
    if login_res.status_code != 200:
        report_logger.error(
            f"Login failed! Status: {login_res.status_code}, Response: {login_res.text}"
        )
        login_res.raise_for_status()

    access_token = login_res.json().get("accessToken")

    # Update headers with bearer token
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    info_res = session.get(f"{cfg.BASE_URL}{cfg.API_VERSION}/auth/info/site-user")
    if info_res.status_code != 200:
        report_logger.error(
            f"Failed to get user info! Status: {info_res.status_code}, Response: {info_res.text}"
        )
        info_res.raise_for_status()

    user_info = info_res.json()
    session.headers.update({"x-fuser-id": str(user_info["fUserId"])})
    # Attach API session id for BaseClient automatic query injection
    session.api_session_id = user_info["sessionId"]

    report_logger.info("Successfully authenticated and session initialized.")
    yield session

    # Teardown so next module does not inherit current user context
    session.headers.pop("Authorization", None)
    session.headers.pop("x-fuser-id", None)
    if hasattr(session, "api_session_id"):
        del session.api_session_id


# --- Layer #3: Main API entry point ---
@pytest.fixture(scope="module")
def api(user_session, cfg):
    """Return a module-scoped ApiClient with auth session and env config."""
    return ApiClient(session=user_session, config=cfg)

