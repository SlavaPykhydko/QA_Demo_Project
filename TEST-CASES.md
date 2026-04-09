# 📋 Test Case: Orders History Contract & Data Integrity

**ID:** `TC-SO-OH-PC-01`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🔥 CRITICAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
API contract and basic data integrity verification during online orders history retrieval. The test ensures that for various order statuses, the backend returns a valid structure (Pydantic validation) and a non-empty list of items.

## 🔑 Preconditions
* Authorized user (with existing Order History).
* User has orders in the following statuses: `ALL`, `DONE`, `CANCEL`, `Active`.

## 🚀 Test Steps

| # | Action                                                                                           | Expected Result |
| :--- |:-------------------------------------------------------------------------------------------------| :--- |
| 1 | Call GET endpoint `/sales/orders/online` with parameters: `page=0`, `limit=40`, `status={status}`. | HTTP status 200. The response successfully passed validation via the Pydantic model. |
| 2 | Verify the length of the retrieved orders list (`items`).                                        | Number of items in the list $len(items) \ge 1$. |
| 3 | Verify the value of the `totalPages` field.                                                      | The value of the $totalPages$ parameter must be $> 0$. |

---

## 📊 Test Data (Parametrization)

The test is executed iteratively for the following status values:

| Iteration ID    | Input Status    | Note               |
|:----------------|:----------------|:-------------------|
| `status_All`    | `Status.ALL`    | All order types    |
| `status_Done`   | `Status.DONE`   | Completed only     |
| `status_Cancel` | `Status.CANCEL` | Cancelled only      |
| `status_Active` | `Status.Active` | Active only        |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestScheme`
* **Test Method:** `test_scheme`

# 📋 Test Case: Pagination & Metadata Validation (List Info)

**ID:** `TC-SO-OH-PC-02`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `pagination`

---

## 🎯 Description
Verification of pagination metadata and list information accuracy. The test ensures that the API correctly calculates `totalCount`, `totalPages`, and page navigation flags (`hasPreviousPage`, `hasNextPage`) by comparing API responses against the actual state of the Database.

## 🔑 Preconditions
* Authorized user with an existing order history.
* User has orders in the following statuses: `ALL`, `DONE`, `CANCEL`, `ACTIVE`.
* Access to the Database (DB) to retrieve actual order counts.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Call GET endpoint `/sales/orders/online` with specific `page`, `limit`, and `status`. | HTTP status 200. |
| 2 | Compare `totalCount` from the API with the actual count from the Database. | `totalCount` matches the DB records for the specific status. |
| 3 | Verify `pageIndex`, `totalPages`, `hasPreviousPage`, and `hasNextPage` flags. | Metadata correctly reflects the current pagination state based on the requested limit and page index. |

---

## 📊 Test Data (Parametrization)

| Iteration ID            | Status   | Page | Limit | Note                           |
|:------------------------|:---------|:---:|:-----:|:--------------------------------------------|
| `All Status`            | `ALL`    | 0 |  40   | All orders fit on one page                  |
| `First Page (Limit 10)` | `ALL`    | 0 |  10   | **⚠️ KNOWN BUG (#1):** Total count mismatch |
| `Last Page (Limit 10)`  | `ALL`    | 2 | 10    | Navigation to the end of the list           |
| `Middle Page (Limit 1)` | `ALL`    | 10 |   1   | High page count navigation                  |
| `Done Status`           | `DONE`   | 0 |  40   |  Status-specific filtering                  |
| `Cancel Status`         | `CANCEL` | 0 |  40   | Status-specific filtering |
| `Active Status`         | `ACTIVE` | 0 |  40   | Status-specific filtering |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestListInfo`
* **Test Method:** `test_list_info_params`

# 📋 Test Case: Order Status Aggregation Consistency

**ID:** `TC-SO-OH-PC-03`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `positive`, `regression`

---

## 🎯 Description
Validation of the mathematical consistency between aggregated order statuses. This test ensures that the total count of orders matches the sum of individual sub-statuses (Done, Canceled, and Active) both in the Database and the API responses.

## 🔑 Preconditions
* Authorized user with an existing order history.
* User has orders in the following statuses: `ALL`, `DONE`, `CANCEL`, `ACTIVE`.
* Database access.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Retrieve total counts for `ALL`, `DONE`, `CANCEL`, and `ACTIVE` statuses via API calls. | All requests return HTTP 200. |
| 2 | Calculate the sum of `Done + Cancel + Active` from the Database records. | The sum equals the `All` count recorded in the DB: <br> $DB_{all} = DB_{done} + DB_{cancel} + DB_{active}$ |
| 3 | Calculate the sum of `Done + Cancel + Active` from the API response fields. | The sum equals the `totalCount` from the `ALL` status API response: <br> $API_{all} = API_{done} + API_{cancel} + API_{active}$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestListInfo`
* **Test Method:** `test_sum_done_cancel_active_orders`

# 📋 Test Case: Order Type Classification Validation

**ID:** `TC-SO-OH-PC-04`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Comprehensive verification of the `type` field for all items in the order history. This test iterates through every single page of the user's history to ensure that every order is correctly classified according to the system's business rules (e.g., "Online" or "Marketplace").

## 🔑 Preconditions
* Authorized user with an existing order history.
* User has orders in the following statuses: `ALL`, `DONE`, `CANCEL`, `ACTIVE`.
* Defined `OrderType` enumeration in the system: `ONLINE` ("Online"), `MARKETPLACE` ("Marketplace").

## 🚀 Test Steps

| # | Action | Expected Result                                               |
| :--- | :--- |:--------------------------------------------------------------|
| 1 | Initialize the expected types list from the `OrderType` enum. | List contains: `['Online', 'Marketplace']`.                   |
| 2 | Use the paginated iterator to retrieve every item across all pages (status: `ALL`, limit: `40`). | API returns successful responses for all pages.               |
| 3 | For each individual item, verify that `item.type` exists within the `expected_types` list. | Every item is associated with a valid, recognized order type. |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestItemType`
* **Test Method:** `test_item_type`

# 📋 Test Case: Response Items Quantity Consistency

**ID:** `TC-SO-OH-PC-05`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `positive`, `regression`

---

## 🎯 Description
Validation of the consistency between the API metadata and the actual response payload. The test ensures that the value returned in the `totalCount` field matches the physical number of items present in the `items` list for a single-page request.

## 🔑 Preconditions
* Authorized user with an existing order history.
* The number of orders for the specific status should not exceed the requested limit (`LIMIT_40`) to ensure a direct 1-to-1 comparison between list length and total count.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Call `get_parsed_items` with status `{status}`, `page=0`, and `limit=40`. | HTTP status 200. Data is successfully parsed into Pydantic models. |
| 2 | Calculate the length of the `items` list: $N = len(items)$. | - |
| 3 | Compare $N$ with the value in the `totalCount` field from the response. | $N == totalCount$ |

---

## 📊 Test Data (Parametrization)

The test is executed for all statuses defined in `STATUS_DATA`:

| Iteration ID    | Input Status | Purpose                                         |
|:----------------|:-------------|:------------------------------------------------|
| `status_All`    | `ALL`        | Check consistency for the full list.            |
| `status_Done`   | `DONE`       | Check consistency for filtered "Done" orders.   |
| `status_Cancel` | `CANCEL`     | Check consistency for filtered "Cancel" orders. |
| `status_Active` | `ACTIVE`     | Check consistency for filtered "Active" orders. |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOnlineOrdersFilterStatus`
* **Test Method:** `test_quantity_items_for_each_status`

# 📋 Test Case: Order Status Mapping & Localization Consistency

**ID:** `TC-SO-OH-PC-06`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Deep verification of status consistency and localization across all pages of the order history. This test ensures two things:
1. The internal `orderStatus` of each item correctly corresponds to the requested filter (e.g., only "RECEIVED" orders appear in the "DONE" filter).
2. The user-facing `status` field (Ukrainian localization) correctly matches the internal `orderStatus` according to the system's translation mapping.

## 🔑 Preconditions
* Authorized user with an order history.
* Defined status mappings in `ORDER_STATUS_MAPPING`.
* Access to `StatusUA` translation enums.

## 🚀 Test Steps

| # | Action                                                                                                                  | Expected Result |
| :--- |:------------------------------------------------------------------------------------------------------------------------| :--- |
| 1 | Iterate through every item across all pages for a `requested_status` (ALL, DONE, CANCEL, ACTIVE).                       | API returns successful responses for all pages. |
| 2 | For each item, verify that `item.orderStatus` is present in the `allowed_statuses` list for that filter.                | Items are correctly filtered by the backend (no status leakage). |
| 3 | For each item, verify that the localized `item.status` (UA) matches the expected translation of its `item.orderStatus`. | Localization is consistent with the internal state: <br> $item.status == item.orderStatus.ukrainian$ |

---

## 📊 Test Data (Status Mapping)
| Requested Filter | Allowed Internal Statuses (`orderStatus`) | Note | UA Localization (`status`) |
|:---|:---|:---|:---|
| `ALL` | `RECEIVED`, `CANCELED`, `ASSEMBLING`, `READY_FOR_PICKUP` | Full history coverage | "Отримано", "Скасовано", "В обробці", "Готово до видачі" |
| `DONE` | `RECEIVED` | Completed orders only | "Отримано" |
| `CANCEL` | `CANCELED` | Cancelled orders only | "Скасовано" |
| `ACTIVE` | `ASSEMBLING`, `READY_FOR_PICKUP` | Active orders only | "В обробці", "Готово до видачі" |
---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOnlineOrdersFilterStatus` (implied)
* **Test Method:** `test_each_item_has_correct_status`

# 📋 Test Case: Order Status Group Classification

**ID:** `TC-SO-OH-PC-07`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Validation of the `statusGroup` parameter consistency across all order history pages. This test ensures that every item is correctly categorized into a logical business group (e.g., `received`, `in_processing`) that strictly corresponds to the requested status filter.

## 🔑 Preconditions
* Authorized user with an order history.
* Defined mapping between `Status` filters and expected `StatusGroup` enum values.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Call the paginated iterator `get_items_with_pagination` for a `requested_status`. | API returns successful responses ($200\ OK$) for all pages. |
| 2 | For each retrieved item, verify that the `statusGroup` field (case-insensitive) is present in the `allowed_statuses` list. | The item's category matches the filter logic (no grouping leakage). |

---

## 📊 Test Data (Status Group Mapping)

| Requested Filter (`status`) | Allowed Status Groups (`statusGroup`) | Note |
|:---|:---|:---|
| `ALL` | `received`, `canceled`, `in_processing`, `ready_for_receive` | Coverage of all possible categories |
| `DONE` | `received` | Only items in the 'Completed' group |
| `CANCEL` | `canceled` | Only items in the 'Cancelled' group |
| `ACTIVE` | `in_processing`, `ready_for_receive` | Items currently being processed or ready |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOnlineOrdersFilterStatus`
* **Test Method:** `test_each_item_has_correct_status_group`


