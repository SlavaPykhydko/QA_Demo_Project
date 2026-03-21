from statistics import mean

import allure
from pytest_check import check

def attach_json(data, name="API Response"):
    allure.attach(
        data.model_dump_json(indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON
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