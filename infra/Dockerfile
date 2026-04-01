# 1. Используем стабильный образ
FROM python:3.10-slim

# 2. Настройка окружения, чтобы логи Python выводились сразу (без буферизации)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 3. Обновляем pip и устанавливаем базовые инструменты
RUN pip install --upgrade pip

# 4. Копируем зависимости
COPY requirements.txt .

# 5. Устанавливаем библиотеки и инструменты OpenTelemetry
RUN pip install --no-cache-dir -r requirements.txt

# Явно ставим датчик для pytest, чтобы агент его точно увидел
RUN pip install opentelemetry-instrumentation-pytest

# КЛЮЧЕВОЙ МОМЕНТ:
# Эта команда увидит, что у тебя установлен pytest и requests,
# и сама скачает для них подходящие opentelemetry-instrumentation-* # (например, версии 0.51b0, которые совместимы с 0.61b0)
RUN opentelemetry-bootstrap -a install

# 2. Добавляем проверку: выведем список установленных плагинов OTel в лог билда
RUN pip list | grep opentelemetry

# 8. Копируем проект
COPY . .

# 9. Создаем папки для отчетов с нужными правами
RUN mkdir -p allure-results junit-reports && chmod -R 777 allure-results junit-reports