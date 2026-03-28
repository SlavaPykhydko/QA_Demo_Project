from statistics import mean
import json
import allure
import re
from pytest_check import check

from src.common.logger import get_log_context


def _build_context_meta(response=None, duration_ms=None):
    context = get_log_context()
    meta = {
        "env": context.get("env", "-"),
        "worker": context.get("worker", "-"),
        "test_nodeid": context.get("test_nodeid", "-"),
        "user_type": context.get("user_type", "-"),
        "request_id": context.get("request_id", "-"),
    }

    if response is not None:
        request = getattr(response, "request", None)
        meta["status_code"] = getattr(response, "status_code", "-")
        meta["method"] = getattr(request, "method", "-") if request else "-"
        meta["url"] = getattr(request, "url", "-") if request else "-"

    if duration_ms is not None:
        meta["duration_ms"] = duration_ms

    return meta


def attach_json(data, name="API Response", response=None, duration_ms=None):
    if hasattr(data, "model_dump"):
        payload_data = data.model_dump()
    else:
        payload_data = data

    attachment_payload = {
        "meta": _build_context_meta(response=response, duration_ms=duration_ms),
        "body": payload_data,
    }

    allure.attach(
        json.dumps(attachment_payload, indent=2, ensure_ascii=False, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )


def attach_curl(response, duration_ms=None):
    if not hasattr(response, 'request'):
        return

    request = response.request
    url = request.url

    # 1. Список ключей, которые мы хотим скрыть
    SENSITIVE_KEYS = ['x-fuser-id', 'authorization', 'token', 'x-api-key', 'session_id', 'cookie']

    # 2. Маскируем данные в URL (Query Parameters)
    # Ищем в URL паттерны типа session_id=abc12345 и заменяем на [MASKED]
    for key in SENSITIVE_KEYS:
        # Регулярка ищет ключ=значение до следующего & или конца строки
        pattern = rf"({key}=)([^&]+)"
        url = re.sub(pattern, r"\1[MASKED]", url)

    # Mask query params using case-insensitive replacement.
    url = re.sub(r"(?i)(session_id=)([^&]+)", r"\1[MASKED]", url)

    # 3. Базовая команда с маскированным URL
    command = f"curl -X {request.method} '{url}'"

    # 3.1 Add context metadata so Allure attachment matches console/file logs.
    meta = _build_context_meta(response=response, duration_ms=duration_ms)
    context_line = (
        f"# env={meta['env']} worker={meta['worker']} test={meta['test_nodeid']} "
        f"user={meta['user_type']} req={meta['request_id']} "
        f"status={meta.get('status_code', '-')} duration_ms={meta.get('duration_ms', '-')}"
    )
    command = f"{context_line}\n{command}"

    # 4. Добавляем заголовки с маскировкой
    ignored_headers = ['User-Agent', 'Accept-Encoding', 'Connection', 'Accept']
    for k, v in request.headers.items():
        if k in ignored_headers:
            continue

        # Если заголовок чувствительный — маскируем
        display_value = "[MASKED]" if any(sk in k.lower() for sk in SENSITIVE_KEYS) else v
        command += f" \\\n  -H '{k}: {display_value}'"

    # 5. Добавляем тело (Body) - там тоже могут быть токены
    if request.body:
        try:
            body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
            # Маскируем и в теле (если там JSON)
            body_str = re.sub(r'(?i)("password"\s*:\s*")[^"]+(")', r'\1[MASKED]\2', body_str)
            body_str = re.sub(r'(?i)("token"\s*:\s*")[^"]+(")', r'\1[MASKED]\2', body_str)
            body_str = re.sub(r'(?i)("session_id"\s*:\s*")[^"]+(")', r'\1[MASKED]\2', body_str)

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