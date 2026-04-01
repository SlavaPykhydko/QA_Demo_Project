FROM python:3.10-slim

# Логи Python будут вылетать в консоль мгновенно
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем инструментацию. Если bootstrap капризничает,
# ставим основные пакеты явно, но БЕЗ фиксации версии.
RUN pip install opentelemetry-instrumentation-pytest \
                opentelemetry-instrumentation-requests \
                opentelemetry-instrumentation-logging

# Финальный прогон для остальных зависимостей
RUN opentelemetry-bootstrap -a install

COPY . .
RUN mkdir -p allure-results junit-reports && chmod -R 777 allure-results junit-reports