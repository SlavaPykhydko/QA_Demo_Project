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
    USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER_PROD")
    USER_PASSWORD = os.getenv("USER_PASSWORD_PROD")
    X_API_KEY = os.getenv("X_API_KEY_PROD")

class StageConfig(Config):
    #Data for Stage
    BASE_URL = os.getenv("BASE_URL_STAGE")
    USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER_STAGE")
    USER_PASSWORD = os.getenv("USER_PASSWORD_STAGE")
    X_API_KEY = os.getenv("X_API_KEY_STAGE")

# Logic config choosing
envs = {
    "PROD": ProdConfig,
    "STAGE": StageConfig
}
 # Default PROD env
env_type = os.getenv("ENV_TYPE", "PROD").upper()
config = envs.get(env_type, ProdConfig)()