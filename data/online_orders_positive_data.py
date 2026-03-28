import allure
import pytest


# Used in TestScheme and TestOnlineOrdersFilterStatus
STATUS_DATA = [
    pytest.param({"status": "All"}, id="status_All"),
    pytest.param({"status": "Done"}, id="status_Done"),
    pytest.param({"status": "Cancel"}, id="status_Cancel"),
]

# Used in TestListInfo
LIST_INFO_DATA = [
    # 1. All orders in one page
    (
        {"page": 0, "limit": 40, "status": "All"},
        {"totalCount": "ALL", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
    # 2. The first page with limit=10 — known bug
    pytest.param(
        {"page": 0, "limit": 10, "status": "All"},
        {"totalCount": "ALL", "totalPages": 3, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": True},
        marks=[
            pytest.mark.xfail(reason="BUG: Total count is wrong", strict=True),
            allure.issue("#Link to Bug #1", "Total count is wrong"),
            allure.description("⚠️ Expected Bug: Total count is wrong. Look at task #1"),
        ],
        id="page_0_limit_10_status=All-BUG",
    ),
    # 3. The last page with limit=10
    (
        {"page": 2, "limit": 10, "status": "All"},
        {"totalCount": "ALL", "totalPages": 3, "pageIndex": 2, "hasPreviousPage": True, "hasNextPage": False},
    ),
    # 4. Some middle page with limit=1
    (
        {"page": 10, "limit": 1, "status": "All"},
        {"totalCount": "ALL", "totalPages": 22, "pageIndex": 10, "hasPreviousPage": True, "hasNextPage": True},
    ),
    # 5. Done orders in one page
    (
        {"page": 0, "limit": 40, "status": "Done"},
        {"totalCount": "DONE", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
    # 6. Cancel orders in one page
    (
        {"page": 0, "limit": 40, "status": "Cancel"},
        {"totalCount": "CANCEL", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
]

# Used in TestOnlineOrdersFilterStatus.test_each_item_has_correct_status
ORDER_STATUS_MAPPING = [
    ("All", ["received", "canceled", "assembling", "readyforpickup"]),
    ("Done", ["received"]),
    ("Cancel", ["canceled"]),
]

# Used in TestOnlineOrdersFilterStatus.test_each_item_has_correct_status_group
STATUS_GROUP_MAPPING = [
    ("All", ["received", "canceled", "in_processing", "ready_for_receive"]),
    ("Done", ["received"]),
    ("Cancel", ["canceled"]),
]

