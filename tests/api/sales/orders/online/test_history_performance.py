import time
import pytest
import allure
import pytest_check as check

pytestmark = [
    pytest.mark.performance,
    allure.epic("Sales & Orders"),
    allure.feature("Orders History"),
    allure.story("Performance checks")
]

class TestPerformance:
    SLA_THRESHOLD = 1.5
    ITERATIONS = 5

    @allure.severity(allure.severity_level.MINOR)
    @allure.title(f"Performance SLA check: Average of {ITERATIONS} requests")
    def test_average_response_time(self, api):
        durations = []

        for i in range(1, self.ITERATIONS + 1):
            with allure.step(f"Iteration {i}: Requesting Online Orders"):
                response = api.online_orders.get_items(page=0, limit=40, status='All')

                check.equal(response.status_code, 200, f"Iteration {i} failed with status {response.status_code}")

                duration = response.elapsed.total_seconds()
                durations.append(duration)

                # Adding attachment for each iteration
                allure.attach(f"Duration: {duration}s", name=f"Attempt {i} result",
                              attachment_type=allure.attachment_type.TEXT)
                time.sleep(0.5)

        api.online_orders._assert_performance_sla(durations=durations, sla_threshold=self.SLA_THRESHOLD)



