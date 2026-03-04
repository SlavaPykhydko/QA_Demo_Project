def test_check_orders_list(online_orders_api):

    expected_total_count = 21
    response = online_orders_api.get_online_orders(page=0, limit=40, status="ALL")

    total_count = online_orders_api._get_json_value(response, "totalCount")
    print(total_count)

    assert total_count == expected_total_count