from src.common.config import config


class TestUser:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        """То, что будет видно в логах при падении и в отчетах"""
        return (f"User(login='{self.login}', "
                f"password='[MASKED]'")

class TestUsers:
    # User who has a rich history (different statuses)
    USER_WITH_HISTORY = TestUser(login=config.USER_PHONE_NUMBER, password=config.USER_PASSWORD)

    # New user without orders (empty state)
    USER_EMPTY = TestUser(login=config.EMPTY_USER_PHONE_NUMBER, password=config.EMPTY_USER_PASSWORD)