def test_check_orders_list(online_orders_api):
    response = online_orders_api.get_online_orders(page=0, limit=40, status="ALL")

    order_id = online_orders_api._get_json_value(response, "data[0].id")

    assert order_id is not None