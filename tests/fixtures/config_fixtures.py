import pytest

from src.common.config import DEFAULT_ENV_NAME, envs


@pytest.fixture(scope="session")
def cfg(request):
    # 1. Getting env from CLI (example: --env=stage)
    env_from_cli = request.config.getoption("--env").upper()

    # 2. Choosing config class from envs dict
    # If unknown env is passed, fallback to default
    config_class = envs.get(env_from_cli, envs[DEFAULT_ENV_NAME])

    # 3. Create and return config object instance
    return config_class()

