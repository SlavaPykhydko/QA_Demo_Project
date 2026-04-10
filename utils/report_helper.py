from statistics import mean
import json
import allure
import re
import functools
from pytest_check import check
from src.common.logger import get_log_context
from src.common.sensitive_keys import SENSITIVE_KEYS


# 1. Допоміжна функція для встановлення динамічних параметрів Allure
def _set_allure_dynamic_parameters(meta: dict):
    """Виносить ключові метадані у верхню секцію Parameters звіту Allure"""
    # Ці параметри буде видно одразу під назвою тесту
    allure.dynamic.parameter("Env", meta.get("env", "-"))
    allure.dynamic.parameter("User Type", meta.get("user_type", "-"))
    if meta.get("worker") != "-":
        allure.dynamic.parameter("Worker", meta.get("worker"))


def _attach_api_context_html(meta: dict):
    # Додаємо font-size: 12px та зменшуємо padding до 4px-6px
    html_content = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border: 1px solid #e1e4e8; border-radius: 6px; padding: 8px; background-color: #fff;">
        <h4 style="margin: 0 0 8px 0; color: #24292e; font-size: 14px;">🚀 API Request Context</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <tr style="background-color: #f6f8fa;">
                <td style="padding: 5px 8px; border: 1px solid #d1d5da; width: 30%;"><b>Method</b></td>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><code>{meta.get('method', '-')}</code></td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><b>Status Code</b></td>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><b style="color: #28a745;">{meta.get('status_code', '-')}</b></td>
            </tr>
            <tr style="background-color: #f6f8fa;">
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><b>Duration</b></td>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;">{meta.get('duration_ms', '-')} ms</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><b>Request ID</b></td>
                <td style="padding: 5px 8px; border: 1px solid #d1d5da;"><code style="font-size: 11px; color: #586069;">{meta.get('request_id', '-')}</code></td>
            </tr>
        </table>
    </div>
    """

    allure.attach(
        html_content,
        name="🚀 API Context",
        attachment_type=allure.attachment_type.HTML
    )


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


# 3. Основний метод для JSON (тепер чистий)
def attach_json(data, name="API Response body", response=None, duration_ms=None):
    # 1. Пріоритет №1: Спочатку прикріплюємо сам JSON
    # Робимо це в першу чергу, щоб ніякі помилки в метаданих не завадили
    try:
        payload_data = data.model_dump() if hasattr(data, "model_dump") else data
        allure.attach(
            json.dumps(payload_data, indent=2, ensure_ascii=False, default=str),
            name=name,
            attachment_type=allure.attachment_type.JSON
        )
    except Exception as e:
        # Якщо навіть JSON впав (наприклад, помилка серіалізації), кріпимо як текст
        allure.attach(f"Error serializing JSON: {e}\nData: {data}",
                      name="FAILED: API Response",
                      attachment_type=allure.attachment_type.TEXT)

    # 2. Пріоритет №2: Метадані та параметри
    # Огортаємо в try-except, щоб помилка в "красі" не ламала звіт
    try:
        meta = _build_context_meta(response=response, duration_ms=duration_ms)

        # Виносимо в параметри
        _set_allure_dynamic_parameters(meta)

        # Створюємо HTML таблицю
        _attach_api_context_html(meta)
    except Exception as e:
        # Друкуємо помилку в консоль для дебагу, але не ламаємо тест
        print(f"\n[ALLURE ERROR] Failed to attach meta-info: {e}")


# 4. Оновлений cURL (без зайвих коментарів, бо вони тепер у Context)
def attach_curl(response, duration_ms=None):
    if not hasattr(response, 'request'):
        return

    request = response.request
    url = request.url

    # Маскування (залишаємо твою логіку)
    for key in SENSITIVE_KEYS:
        url = re.sub(rf"({key}=)([^&]+)", r"\1[MASKED]", url)
    url = re.sub(r"(?i)(session_id=)([^&]+)", r"\1[MASKED]", url)

    command = f"curl -X {request.method} '{url}'"

    # Додаємо заголовки
    ignored_headers = ['User-Agent', 'Accept-Encoding', 'Connection', 'Accept']
    for k, v in request.headers.items():
        if k in ignored_headers: continue
        display_value = "[MASKED]" if any(sk in k.lower() for sk in SENSITIVE_KEYS) else v
        command += f" \\\n  -H '{k}: {display_value}'"

    # Додаємо Body
    if request.body:
        try:
            body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
            # Твоє маскування в JSON...
            body_json = json.loads(body_str)
            payload = json.dumps(body_json, indent=2, ensure_ascii=False)
            command += f" \\\n  -d '{payload}'"
        except:
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


def link_to_case(case_id: str):
    """
    Формує повне посилання на тест-кейс у GitHub.
    Автоматично переводить ID у нижній регістр для роботи якорів GitHub.
    """
    base_url = "https://github.com/SlavaPykhydko/QA_Demo_Project/blob/main/tests/api/sales/orders/online/TEST-CASES.md"
    # GitHub робить якоря (anchors) маленькими літерами
    anchor = case_id.lower()

    # Використовуємо dynamic.link, щоб зашити ПОВНИЙ URL у звіт
    allure.dynamic.link(
        url=f"{base_url}#{anchor}",
        name=case_id,
        link_type="tms"
    )

def github_tc(case_id):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Вызываем твой хелпер автоматически перед тестом
            link_to_case(case_id)
            return func(*args, **kwargs)
        return wrapper
    return decorator