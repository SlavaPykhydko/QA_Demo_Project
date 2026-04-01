#!/bin/bash

# 1. Smoke
pytest -m smoke --env=${TARGET_ENV:-prod} --alluredir=allure-results --clean-alluredir --junitxml=junit-reports/report_smoke.xml -n ${THREADS:-2}

# 2. Regression (уже БЕЗ --clean-alluredir)
pytest -m "regression and not smoke" --env=${TARGET_ENV:-prod} --alluredir=allure-results --junitxml=junit-reports/report_regression.xml -n ${THREADS:-2}

# 3. Performance
pytest -m performance --env=${TARGET_ENV:-prod} --alluredir=allure-results --junitxml=junit-reports/report_performance.xml -n ${THREADS:-2}