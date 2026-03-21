from enum import Enum


class UserType(Enum):
    WITH_HISTORY = "with_history"
    EMPTY = "empty"

class UserAccount:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        """It will be shown in the logs during a crash and in reports"""
        return (f"User(login='{self.login}', "
                f"password='[MASKED]'")

class UserFactory:
    @staticmethod
    def get_user(user_type: UserType, cfg):
        """Фабрика, яка створює об'єкт юзера на основі поточного конфігу"""
        if user_type == UserType.WITH_HISTORY:
            return UserAccount(login=cfg.USER_PHONE_NUMBER, password=cfg.USER_PASSWORD)
        if user_type == UserType.EMPTY:
            return UserAccount(login=cfg.EMPTY_USER_PHONE_NUMBER, password=cfg.EMPTY_USER_PASSWORD)
        raise ValueError(f"Unknown user type: {user_type}")

# class UserAccounts:
#     # User who has a rich history (different statuses)
#     USER_WITH_HISTORY = UserAccount(login=config.USER_PHONE_NUMBER, password=config.USER_PASSWORD)
#
#     # New user without orders (empty state)
#     USER_EMPTY = UserAccount(login=config.EMPTY_USER_PHONE_NUMBER, password=config.EMPTY_USER_PASSWORD)