import allure

def attach_json(data, name="API Response"):
    allure.attach(
        data.model_dump_json(indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )