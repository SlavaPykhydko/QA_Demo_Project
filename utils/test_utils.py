def generate_test_name(val):
    """
    Универсальный генератор имен для параметризованных тестов.
    Пытается собрать красивую строку из словаря с параметрами.
    """
    if isinstance(val, dict):
        # Собираем ключи, которые часто используются (limit, page, status и т.д.)
        parts = []
        for key in ["limit", "page", "status", "type"]:
            if key in val:
                parts.append(f"{key}_{val[key]}")

        return "-".join(parts) if parts else None

    # Для всех остальных типов данных (строки, числа) Pytest сам справится
    return None