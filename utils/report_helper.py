from statistics import mean
import json
import allure
import re
from pytest_check import check


def attach_json(data, name="API Response"):
    allure.attach(
        data.model_dump_json(indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )


def attach_curl(response):
    if not hasattr(response, 'request'):
        return

    request = response.request
    url = request.url

    # 1. Список ключей, которые мы хотим скрыть
    SENSITIVE_KEYS = ['x-fuser-id', 'Authorization', 'token', 'x-api-key']

    # 2. Маскируем данные в URL (Query Parameters)
    # Ищем в URL паттерны типа session_id=abc12345 и заменяем на [MASKED]
    for key in SENSITIVE_KEYS:
        # Регулярка ищет ключ=значение до следующего & или конца строки
        pattern = rf"({key}=)([^&]+)"
        url = re.sub(pattern, r"\1[MASKED]", url)

    # 3. Базовая команда с маскированным URL
    command = f"curl -X {request.method} '{url}'"

    # 4. Добавляем заголовки с маскировкой
    ignored_headers = ['User-Agent', 'Accept-Encoding', 'Connection', 'Accept']
    for k, v in request.headers.items():
        if k in ignored_headers:
            continue

        # Если заголовок чувствительный — маскируем
        display_value = "[MASKED]" if any(sk.lower() in k.lower() for sk in SENSITIVE_KEYS) else v
        command += f" \\\n  -H '{k}: {display_value}'"

    # 5. Добавляем тело (Body) - там тоже могут быть токены
    if request.body:
        try:
            body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
            # Маскируем и в теле (если там JSON)
            for key in SENSITIVE_KEYS:
                body_str = re.sub(rf'("{key}":\s*")[^"]+(")', r'\1[MASKED]\2', body_str)

            # Форматируем JSON для красоты
            body_json = json.loads(body_str)
            payload = json.dumps(body_json, indent=2, ensure_ascii=False)
            command += f" \\\n  -d '{payload}'"
        except (ValueError, TypeError):
            command += f" \\\n  -d '{request.body}'"

    allure.attach(
        command,
        name="Request cURL",
        attachment_type=allure.attachment_type.TEXT,
        extension="txt"
    )

def assert_performance_sla(durations, sla_threshold):
    # 2. Calculate statistics
    avg_time = mean(durations)
    max_time = max(durations)
    min_time = min(durations)

    # 3. Data output to Allure parameters
    allure.dynamic.parameter("Average Time", f"{avg_time:.3f}s")
    allure.dynamic.parameter("Max Time", f"{max_time:.3f}s")
    allure.dynamic.parameter("Min Time", f"{min_time:.3f}s")
    allure.dynamic.parameter("SLA Limit", f"{sla_threshold}s")

    with allure.step(f"Verify Average Response Time ({avg_time:.3f}s) < SLA ({sla_threshold}s)"):
        check.less(
            avg_time,
            sla_threshold,
            f"Average response time is too high! Avg: {avg_time:.3f}s, Threshold: {sla_threshold}s"
        )