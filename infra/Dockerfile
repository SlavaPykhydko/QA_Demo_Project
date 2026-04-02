FROM python:3.10-slim

# Логи будут выводиться сразу
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Обновляем инструменты сборки
RUN pip install --upgrade pip setuptools wheel

# Копируем только требования для установки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- СЕКРЕТНЫЙ ИНГРЕДИЕНТ ---
# Вместо ручной установки пакетов, которые pip "не видит",
# мы просим bootstrap поставить ВСЁ, что подходит под твои установленные библиотеки.
RUN opentelemetry-bootstrap -a install

COPY . .

# 2. ДЕЛАЕМ СКРИПТ ВЫПОЛНЯЕМЫМ
# Это критически важный шаг, иначе Docker выдаст "Permission denied"
RUN chmod +x entrypoint.sh

# Создаем папки для отчетов
RUN mkdir -p allure-results junit-reports && chmod -R 777 allure-results junit-reports