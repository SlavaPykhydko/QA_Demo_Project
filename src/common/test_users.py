class TestUsers:
    # Юзер с богатой историей (разные статусы)
    USER_WITH_HISTORY = {
        "email": "user_history@example.com",
        "password": "Password123",
        "expected_counts": {"Done": 19, "Cancel": 2, "All": 21}
    }

    # Новый юзер без заказов (пустое состояние)
    USER_EMPTY = {
        "email": "user_empty@example.com",
        "password": "Password123",
        "expected_counts": {"Done": 0, "Cancel": 0, "All": 0}
    }