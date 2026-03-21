import allure
from pytest_check import check


class AssertionsMixin:
    def _assert_problem_details(self, response, expected_title="validation errors occurred"):
        """" Checking the response structure according to RFC 9110 (Problem Details). """

        data = response.json()

        with allure.step("Verify standard Problem Details (RFC 9110)"):
            check.equal(response.status_code, 400, "HTTP Header status code != 400")
            check.equal(data.get("status"), 400, "JSON 'status' field != 400")

            actual_title = data.get("title", "")
            check.is_in(expected_title, actual_title,
                        f"Expected title part '{expected_title}' not found in '{actual_title}'")

            trace_id = data.get("traceId", "")
            check.greater(len(str(trace_id)), 54, f"traceId is missing or suspiciously short: '{trace_id}'")
