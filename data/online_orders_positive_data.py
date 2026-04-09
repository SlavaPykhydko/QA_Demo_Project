import allure
import pytest
from src.common.enums.orders import Status, OrderStatus, StatusGroup

# Used in TestScheme and TestOnlineOrdersFilterStatus
STATUS_DATA = [
    pytest.param({"status": Status.ALL}, id="status_All"),
    pytest.param({"status": Status.DONE}, id="status_Done"),
    pytest.param({"status": Status.CANCEL}, id="status_Cancel"),
    # pytest.param({"status": Status.ACTIVE}, id="status_Active")
]

# Used in TestListInfo
LIST_INFO_DATA = [
    # 1. All orders in one page
    (
        {"page": 0, "limit": 40, "status": Status.ALL},
        {"totalCount": "all", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
    # 2. The first page with limit=10 — known bug
    pytest.param(
        {"page": 0, "limit": 10, "status": Status.ALL},
        {"totalCount": "all", "totalPages": 3, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": True},
        marks=[
            pytest.mark.xfail(reason="BUG: Total count is wrong", strict=True),
            allure.issue("#Link to Bug #1", "Total count is wrong"),
            allure.description("⚠️ Expected Bug: Total count is wrong. Look at task #1"),
        ],
        id="page_0_limit_10_status=All-BUG",
    ),
    # 3. The last page with limit=10
    (
        {"page": 2, "limit": 10, "status": Status.ALL},
        {"totalCount": "all", "totalPages": 3, "pageIndex": 2, "hasPreviousPage": True, "hasNextPage": False},
    ),
    # 4. Some middle page with limit=1
    (
        {"page": 10, "limit": 1, "status": Status.ALL},
        {"totalCount": "all", "totalPages": 22, "pageIndex": 10, "hasPreviousPage": True, "hasNextPage": True},
    ),
    # 5. Done orders in one page
    (
        {"page": 0, "limit": 40, "status": Status.DONE},
        {"totalCount": "done", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
    # 6. Cancel orders in one page
    (
        {"page": 0, "limit": 40, "status": Status.CANCEL},
        {"totalCount": "cancel", "totalPages": 1, "pageIndex": 0, "hasPreviousPage": False, "hasNextPage": False},
    ),
]

# Used in TestOnlineOrdersFilterStatus.test_each_item_has_correct_status
ORDER_STATUS_MAPPING = [
    (Status.ALL, [OrderStatus.RECEIVED, OrderStatus.CANCELED, OrderStatus.ASSEMBLING, OrderStatus.READY_FOR_PICKUP]),
    (Status.DONE, [OrderStatus.RECEIVED]),
    (Status.CANCEL, [OrderStatus.CANCELED]),
    # (Status.ACTIVE, [OrderStatus.ASSEMBLING, OrderStatus.READY_FOR_PICKUP]),
]

# Used in TestOnlineOrdersFilterStatus.test_each_item_has_correct_status_group
STATUS_GROUP_MAPPING = [
    (Status.ALL, [StatusGroup.RECEIVED, StatusGroup.CANCELED, StatusGroup.IN_PROCESSING, StatusGroup.READY_FOR_RECEIVE]),
    (Status.DONE, [StatusGroup.RECEIVED]),
    (Status.CANCEL, [StatusGroup.CANCELED]),
    # (Status.ACTIVE, [StatusGroup.IN_PROCESSING, StatusGroup.READY_FOR_RECEIVE]),
]

