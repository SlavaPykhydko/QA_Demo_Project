# 1. Используем стабильный образ
FROM python:3.10-slim

# 2. Настройка окружения, чтобы логи Python выводились сразу (без буферизации)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 3. Обновляем pip и устанавливаем базовые инструменты
RUN pip install --upgrade pip

# 4. Копируем зависимости
COPY requirements.txt .

# 5. Устанавливаем библиотеки и инструменты OpenTelemetry
RUN pip install --no-cache-dir -r requirements.txt

# 6. Явно устанавливаем инструментацию для pytest и requests.
# Это критично, чтобы агент "увидел" твои тесты и запросы.
RUN pip install opentelemetry-instrumentation-pytest==0.61b0 \
                opentelemetry-instrumentation-requests==0.61b0 \
                opentelemetry-instrumentation-logging==0.61b0

# 7. Финальный bootstrap для подхвата остальных библиотек (urllib3 и т.д.)
RUN opentelemetry-bootstrap -a install

# 8. Копируем проект
COPY . .

# 9. Создаем папки для отчетов с нужными правами
RUN mkdir -p allure-results