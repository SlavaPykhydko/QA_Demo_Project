# 📋 Test Case: Orders History Contract & Data Integrity

#### **ID:** `TC-SO-OH-PC-01`  
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

#### **ID:**`TC-SO-OH-PC-03`  
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

# 📋 Test Case: Checking sum qnt items from all pages

**ID:** `TC-SO-OH-PC-08`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
A full data reconciliation check between the API and the Database. The test iterates through every single page of the order history, collects all retrieved items into a single list, and verifies that the final count perfectly matches the total number of records stored in the Database.

## 🔑 Preconditions
* Authorized user with an order history.
* Access to the Database.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Execute a paginated crawl using `get_items_with_pagination` for `Status.ALL` with a limit of 40. | Every page returns a successful $200\ OK$ response. |
| 2 | Aggregate all items retrieved from all pages into a single collection. | No items are lost or duplicated during the iteration process. |
| 3 | Compare the total count of aggregated items ($N$) with the `all` count from the Database ($DB_{all}$). | $N == DB_{all}$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestQntAllItemsViaPagination`
* **Test Method:** `test_sum_qnt_items_from_all_pages`

# 📋 Test Case: Seller Identity & Order Type Consistency

**ID:** `TC-SO-OH-PC-09`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `positive`, `business-logic`, `data-integrity`, `pagination`

---

## 🎯 Description
Verification of the logical mapping between the order's `seller` and its `type`. The test enforces a strict business rule: any order sold by the primary entity ("Епіцентр К") must be classified as an `Online` order, while any other seller must result in a `Marketplace` classification.

## 🔑 Preconditions
* Authorized user with an order history containing both primary and third-party sellers.
* Defined `OrderType` enumeration: `ONLINE` ("Online"), `MARKETPLACE` ("Marketplace").
* Primary seller identifier: `"епіцентр к"`.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses for all pages. |
| 2 | Convert `item.seller` to lowercase and check if it matches "епіцентр к". | - |
| 3 | If the seller is the primary entity, verify that `item.type == "Online"`. | Correct classification for internal sales. |
| 4 | If the seller is any other entity, verify that `item.type == "Marketplace"`. | Correct classification for third-party sales. |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestSellerConsistency`
* **Test Method:** `test_seller_and_selling_type_consistency`

# 📋 Test Case: Global Order ID Uniqueness Across Pagination

**ID:** `TC-SO-OH-PC-10`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Verification of the global uniqueness of Order IDs across the entire history dataset. This test ensures that as the system paginates through results, no single order is duplicated or returned multiple times on different pages, which would indicate a flaw in the backend's sorting or offset logic.

## 🔑 Preconditions
* Authorized user with an order history.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Execute a full crawl of the order history using `get_items_with_pagination` for `Status.ALL`. | All pages are retrieved successfully ($200\ OK$). |
| 2 | Collect every `item.id` from every page into a single master list. | - |
| 3 | Compare the total number of collected IDs with the number of unique IDs. | The counts are equal: <br> $len(all\_ids) == len(set(all\_ids))$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestIdsUniqueness`
* **Test Method:** `test_ids_uniqueness`

# 📋 Test Case: Global Order Sorting (Newest First)

**ID:** `TC-SO-OH-PC-11`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Verification of the chronological sorting of the order history. The test ensures that all orders across all pages are returned in descending order (newest to oldest) based on their creation date (`createdOn`).

## 🔑 Preconditions
* Authorized user with an order history spanning different dates.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Execute a full crawl of the order history using `get_items_with_pagination` for `Status.ALL`. | All pages are retrieved successfully ($200\ OK$). |
| 2 | Collect all `createdOn` timestamps into an `actual_dates` list. | - |
| 3 | Create an `expected_dates` list by sorting the collected dates in descending order. | - |
| 4 | Compare `actual_dates` with `expected_dates`. | The lists are identical, confirming the "Newest First" sorting. |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOrdersSorting`
* **Test Method:** `test_item_sorting_by_date`

# 📋 Test Case: Order Image Asset Integrity & Availability

**ID:** `TC-SO-OH-PC-12`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Comprehensive verification of image assets for all items in the order history. This test ensures that every image URL provided by the API follows the required naming conventions (prefix and extension) and is physically accessible (HTTP 200) via a high-performance multi-threaded check.

## 🔑 Preconditions
* Authorized user with anorder history containing product images.
* Access to `URL_PREFIX` in the configuration.
* Defined `ALLOWED_IMAGE_EXTENSIONS` ( `.jpg`, `.jpeg`).

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses for all pages. |
| 2 | For each image URL in `item.goods`, verify the string prefix against `cfg.URL_PREFIX`. | URL starts with the correct CDN/Server prefix. |
| 3 | Verify the file extension against the allowed list. | URL ends with a valid image extension. |
| 4 | Perform an HTTP HEAD request for each URL using a thread pool (max workers: 10). | Every request returns HTTP status `200 OK`. |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOnlineOrdersImage`
* **Test Method:** `test_image_is_not_broken`

# 📋 Test Case: Order Price Positive Value Validation

**ID:** `TC-SO-OH-PC-13`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Verification of the monetary value integrity for every order. This test iterates through the entire order history to ensure that no order has a price of zero or a negative value, which would indicate a critical data integrity issue or a failure in the price calculation logic.

## 🔑 Preconditions
* Authorized user with an order history.
* Every order in the system must have a recorded transaction price $> 0$.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses for all pages. |
| 2 | For each retrieved item, check the value of the `price` parameter. | The price is a numeric value greater than zero: <br> $item.price > 0$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOrderPrice`
* **Test Method:** `test_item_price_param`

# 📋 Test Case: Order Item Quantity Validation

**ID:** `TC-SO-OH-PC-14`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Verification of the quantity parameter for every item in the order history. This test ensures that every record contains a valid, positive number of items ($> 0$), preventing data corruption issues where orders might appear with empty or zero-count contents.

## 🔑 Preconditions
* Authorized user with an order history.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses ($200\ OK$) for all pages. |
| 2 | For each retrieved item, check the value of the `quantity` parameter. | The quantity is a numeric value greater than zero: <br> $item.quantity > 0$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestQuantityParam`
* **Test Method:** `test_item_qnt_param`

# 📋 Test Case: Product Quantity vs. Asset Count Consistency

**ID:** `TC-SO-OH-PC-15`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression` 

---

## 🎯 Description
Verification of the integrity between the declared item quantity and the number of associated product assets. This test ensures that for every order, the `quantity` value matches the actual count of image URLs provided in the `goods` array, preventing discrepancies between numerical metadata and visual data.

## 🔑 Preconditions
* Authorized user with an order history.
* Business rule requirement: each individual unit in an order must be represented by a corresponding entry in the `goods` image array.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses ($200\ OK$) for all pages. |
| 2 | Calculate the length of the `item.goods` array ($L$). | - |
| 3 | Compare $L$ with the value of the `item.quantity` parameter. | The number of images matches the quantity: <br> $len(item.goods) == item.quantity$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestGoodsAndImageConsistency`
* **Test Method:** `test_item_qnt_param_equal_image_qnt`

# 📋 Test Case: Order ID & Name Identity Consistency

**ID:** `TC-SO-OH-PC-16`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
Verification of the identity mapping between the order's unique identifier (`id`) and its display name (`name`). This test ensures that for every order record, the `name` field is an exact string match of the `id` field, maintaining consistency between technical identifiers and user-facing labels.

## 🔑 Preconditions
* Authorized user with an order history.
* Business rule requirement: The `name` property must serve as the string-based alias for the numeric or UUID `id`.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Iterate through every order across all pages using `get_items_with_pagination`. | API returns successful responses ($200\ OK$) for all pages. |
| 2 | Convert the `item.id` to a string representation. | - |
| 3 | Compare the stringified ID with the `item.name` value. | Both values are identical: <br> $str(item.id) == item.name$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestIdAndNameConsistency`
* **Test Method:** `test_id_and_name_consistency`

# 📋 Test Case: API vs. Database Deep Data Reconciliation

**ID:** `TC-SO-OH-PC-17`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `smoke`, `positive`, `regression`

---

## 🎯 Description
End-to-end data integrity verification by performing a field-by-field comparison between the API response and the Database (DB) records. This test ensures that the backend correctly retrieves and maps persistent data into the API payload without data loss or incorrect transformations.

## 🔑 Preconditions
* Authorized user with an order history.
* Access to the Database.
* Defined `EXCLUDE_FIELDS` (fields that are expected to differ or be transformed, e.g., `createdOn`, `goods`).

## 🚀 Test Steps

| # | Action                                                                                                                                | Expected Result |
| :--- |:--------------------------------------------------------------------------------------------------------------------------------------| :--- |
| 1 | Crawl all pages for `Status.CANCEL` (just in this case, for real project it will be Status.ALL) orders using the pagination iterator. | API returns successful responses ($200\ OK$). |
| 2 | For each `api_item`, attempt to find the matching record in the Database map by ID.                                                   | Every item returned by the API exists in the Database. |
| 3 | Transform both API and DB objects into dictionaries (Pydantic `model_dump`).                                                          | Data structures are ready for comparison. |
| 4 | Iterate through all fields (except excluded ones) and compare values.                                                                 | Values in the API match the values in the Database: <br> $API_{field} == DB_{field}$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestOrderDataEqualDataFromDB`
* **Test Method:** `test_order_data_equal_data_from_db`

# 📋 Test Case: Default Status Parameter Validation

**ID:** `TC-SO-OH-PC-18`  
**Epic:** Sales & Orders  
**Feature:** Orders History  
**Story:** Positive checks  
**Severity:** 🟡 NORMAL  
**Tags:** `positive`, `defaults`, `regression`

---

## 🎯 Description
Verification of the API's default behavior when the `status` parameter is omitted from the request. This test ensures that the system correctly defaults to `Status.ALL`, returning the full history of orders rather than failing or returning an empty set.

## 🔑 Preconditions
* Authorized user with an existing order history.
* Database access.

## 🚀 Test Steps

| # | Action | Expected Result |
| :--- | :--- | :--- |
| 1 | Call the `get_parsed_items` method with `page=0` and `limit=40`, but **without** providing a `status` parameter. | HTTP status 200. Data is successfully parsed into Pydantic models. |
| 2 | Verify that the returned `items` list is not empty. | At least one item is returned ($len(items) \ge 1$). |
| 3 | Compare the `totalCount` from the response with the `all` count from the Database ($DB_{all}$). | The counts match, confirming the default filter is `ALL`: <br> $API_{totalCount} == DB_{all}$ |

---

## 🛠 Technical Implementation Details

* **Test Class:** `TestDefaultsParams`
* **Test Method:** `test_default_status_is_all`

