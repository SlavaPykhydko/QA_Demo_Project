import time
import responses
import pytest
import requests
from src.api.base_client import BaseClient


@responses.activate
def test_retry_logic_with_mock(cfg):
    """
    Тест перевіряє механізм ретраїв BaseClient без авторизації.
    """
    # Створюємо базовий клієнт (він не робить Login!)
    client = BaseClient(cfg)

    # Використовуємо full_url, який точно є в BaseClient
    test_url = f"{client.full_url}/test-retry"

    # Налаштовуємо мок: 3 спроби повертають 500, четверта — 200
    responses.add(responses.GET, test_url, status=500)
    responses.add(responses.GET, test_url, status=500)
    responses.add(responses.GET, test_url, status=500)
    responses.add(responses.GET, test_url, json={"status": "recovered"}, status=200)

    # Викликаємо метод (має спрацювати після 3-х ретраїв)
    response = client._get("test-retry")

    assert response.status_code == 200
    assert response.json()["status"] == "recovered"

    # ПЕРЕВІРКА: 1 основний запит + 3 ретраї = 4 виклики
    assert len(responses.calls) == 4
    print(f"\n[INFO] Успішно! Зроблено спроб: {len(responses.calls)}")


def test_retry_backoff_real_world(cfg):
    client = BaseClient(cfg)
    # Ендпоінт, який завжди повертає 500
    # ВАЖЛИВО: не використовуйте @responses.activate тут!
    client.full_url = "https://httpbin.org"

    start_time = time.time()
    try:
        client._get("/status/500")
    except Exception:
        pass

    execution_time = time.time() - start_time
    print(f"\n[INFO] Реальний час з ретраями: {execution_time}с")

    # При total=3 та backoff=1: 1с + 2с + 4с = має бути мінімум 7 секунд
    assert execution_time > 6


import pytest
import requests
import time


def test_timeout_actually_stops_request(cfg):
    client = BaseClient(cfg)
    client.full_url = "https://httpbin.org"
    client.default_timeout = 2

    # Вимикаємо ретраї для цього тесту, щоб перевірити ЧИСТИЙ таймаут
    # Це прибере затримку в 16 секунд
    client.retry_count = 0
    client._setup_retry_policy()

    start_time = time.time()

    # Ловимо ConnectionError, бо requests при таймауті з ретраями видає її
    # Або вказуємо кортеж помилок (Timeout, ConnectionError)
    with pytest.raises((requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        client._get("/delay/5")

    execution_time = time.time() - start_time

    # Тепер тест пройде за ~2 секунди
    assert execution_time < 3, f"Таймаут не спрацював! Чекали {execution_time}с"
    print(f"\n[INFO] Чистий таймаут спрацював за {execution_time:.2f}с")