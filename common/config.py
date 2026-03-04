import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://mobile-api.epicentrk.ua"
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER")
USER_PASSWORD = os.getenv("USER_PASSWORD")
X_API_KEY = os.getenv("X_API_KEY")
