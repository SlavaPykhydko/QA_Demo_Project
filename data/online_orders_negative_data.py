import allure
import pytest


NEGATIVE_STATUS_DATA = [
    pytest.param({"status": "Unknown"}, id="status_as_random_string"),
    pytest.param({"status": -1}, id="status_as_int"),
    pytest.param({"status": ""}, id="status_as_empty_string"),
    pytest.param({"status": "12345"}, id="status_as_numeric_string"),
    pytest.param({"status": "\0"}, id="status_as_null_byte"),
    pytest.param({"status": True}, id="status_as_boolean"),
    pytest.param({"status": "Deleted"}, id="status_as_deleted"),
]

NEGATIVE_PAGE_DATA = [
    pytest.param({"page": "Unknown"}, id="page_as_random_string"),
    pytest.param(
        {"page": -1},
        id="page_as_negative_int_value",
        marks=[
            pytest.mark.xfail(
                reason="BUG: Online orders history. Server error when page=-1",
                strict=True,
            ),
            allure.issue(
                "#Link to Bug #2",
                "Online orders history. Server error when page=-1",
            ),
            allure.description(
                "Expected Bug: Online orders history. Server error when page=-1. "
                "Look at task #2"
            ),
        ],
    ),
    pytest.param({"page": ""}, id="page_as_empty_string"),
    pytest.param({"page": "\0"}, id="page_as_null_byte"),
    pytest.param({"page": True}, id="page_as_boolean"),
]

