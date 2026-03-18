from src.common.config import config


class UserAccount:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        """It will be shown in the logs during a crash and in reports"""
        return (f"User(login='{self.login}', "
                f"password='[MASKED]'")

class UserAccounts:
    # User who has a rich history (different statuses)
    USER_WITH_HISTORY = UserAccount(login=config.USER_PHONE_NUMBER, password=config.USER_PASSWORD)

    # New user without orders (empty state)
    USER_EMPTY = UserAccount(login=config.EMPTY_USER_PHONE_NUMBER, password=config.EMPTY_USER_PASSWORD)