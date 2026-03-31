# 1. Вибираємо легкий образ Python
FROM python:3.10-slim

# 2. Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# 3. Копіюємо файл з залежностями (це робиться окремо для кешування)
COPY requirements.txt .

# 4. устанавливаем библиотеки 
#Эта команда сама просканирует твои установленные пакеты (pytest, requests) и доставит нужные дополнения для OpenTelemetry нужных версий.
RUN pip install --no-cache-dir -r requirements.txt
RUN opentelemetry-bootstrap -a install

# 5. Копіюємо весь проект у контейнер
COPY . .

# 6. Створюємо папку для звітів (щоб Docker не мав проблем з правами)
RUN mkdir -p allure-results
