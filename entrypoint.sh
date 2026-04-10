#!/bin/bash

# Останавливать выполнение, если команда вернула ошибку (аналог &&)
set -e

echo "🚀 Starting Test Suites..."

# 1. Smoke Tests (Очищаем папку allure-results перед началом)
echo "--- Running Smoke Tests ---"
pytest -m smoke \
    --env=${TARGET_ENV:-prod} \
    --alluredir=allure-results \
    --clean-alluredir \
    --junitxml=junit-reports/report_smoke.xml \
    -n ${THREADS:-2}

## 2. Regression Tests (Дописываем результаты в ту же папку)
#echo "--- Running Regression Tests ---"
#pytest -m "regression and not smoke" \
#    --env=${TARGET_ENV:-prod} \
#    --alluredir=allure-results \
#    --junitxml=junit-reports/report_regression.xml \
#    -n ${THREADS:-2}
#
## 3. Performance Tests
#echo "--- Running Performance Tests ---"
#pytest -m performance \
#    --env=${TARGET_ENV:-prod} \
#    --alluredir=allure-results \
#    --junitxml=junit-reports/report_performance.xml \
#    -n ${THREADS:-2}
#
#echo "✅ All suites finished!"