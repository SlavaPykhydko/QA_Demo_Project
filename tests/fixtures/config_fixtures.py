import pytest

from src.common.config import envs


_REQUIRED_CFG_FIELDS = (
    "BASE_URL",
    "X_API_KEY",
    "URL_PREFIX",
    "USER_PHONE_NUMBER",
    "USER_PASSWORD",
    "EMPTY_USER_PHONE_NUMBER",
    "EMPTY_USER_PASSWORD",
)


def _validate_required_fields(config, env_name: str):
    missing = [
        field for field in _REQUIRED_CFG_FIELDS if not str(getattr(config, field, "")).strip()
    ]
    if missing:
        raise pytest.UsageError(
            "Missing required configuration values for "
            f"--env={env_name.lower()}: {', '.join(missing)}. "
            "Fill them in .env (see .env.example)."
        )


@pytest.fixture(scope="session")
def cfg(request):
    # 1. Getting env from CLI (example: --env=stage)
    env_from_cli = request.config.getoption("--env").upper().strip()

    # 2. Create config object and validate required values before tests run
    config = envs[env_from_cli]()
    _validate_required_fields(config, env_from_cli)
    return config
