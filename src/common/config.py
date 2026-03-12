import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #common system settings
    API_VERSION = "/api/v2"
    PLATFORM = "ios"
    MOBILE_VERSION = "4.9.2122"

class ProdConfig(Config):
    #Data for Production
    BASE_URL = os.getenv("BASE_URL_PROD")
    X_API_KEY = os.getenv("X_API_KEY_PROD")
    # user data
    USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER_PROD")
    USER_PASSWORD = os.getenv("USER_PASSWORD_PROD")

    EMPTY_USER_PHONE_NUMBER = os.getenv("EMPTY_USER_PHONE_NUMBER_PROD")
    EMPTY_USER_PASSWORD = os.getenv("EMPTY_USER_PASSWORD_PROD")

    # Data for DB
    DB_HOST = os.getenv("DB_HOST_PROD")
    DB_PORT = os.getenv("DB_PORT_PROD")
    DB_USER = os.getenv("DB_USER_PROD")
    DB_PASSWORD = os.getenv("DB_PASSWORD_PROD")
    DB_NAME = os.getenv("DB_NAME_PROD")

class StageConfig(Config):
    #Data for Stage
    BASE_URL = os.getenv("BASE_URL_STAGE")
    USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER_STAGE")
    USER_PASSWORD = os.getenv("USER_PASSWORD_STAGE")
    X_API_KEY = os.getenv("X_API_KEY_STAGE")
    # Data for DB
    DB_HOST = os.getenv("DB_HOST_STAGE")
    DB_PORT = os.getenv("DB_PORT_STAGE")
    DB_USER = os.getenv("DB_USER_STAGE")
    DB_PASSWORD = os.getenv("DB_PASSWORD_STAGE")
    DB_NAME = os.getenv("DB_NAME_STAGE")

# Logic config choosing
envs = {
    "PROD": ProdConfig,
    "STAGE": StageConfig
}
 # Default PROD env
env_type = os.getenv("ENV_TYPE", "PROD").upper()
config = envs.get(env_type, ProdConfig)()