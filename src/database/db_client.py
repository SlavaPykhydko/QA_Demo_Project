from sqlalchemy import create_engine, text, URL

class BaseDBClient:
    def get_online_orders_counts(self):
        # This method MUST be overridden in subclasses.
        raise NotImplementedError("The method must be implemented in subclasses")

class DBClient(BaseDBClient):
    def __init__(self, cfg):
        # Creating a connection URL via object (when there are all parameters)
        self.connection_url = URL.create(
            drivername="postgresql",  # or "mssql+pyodbc", "mysql+pymysql" etc
            username=cfg.DB_USER,
            password=cfg.DB_PASSWORD,
            host=cfg.DB_HOST,
            port=cfg.DB_PORT,
            database=cfg.DB_NAME
        )
        # if echo=True  SQL-queries will be written to logs
        self.engine = create_engine(self.connection_url, echo=False)

    def execute_query(self, query):
        # Method for execution any SQL query
        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            return result.fetchall()

    def get_online_orders_counts(self):
        # Here will be the actual SQL query when access becomes available.
        query = "some query"
        # result = self.execute_query(query)
        # return transform_to_dict(result)
        pass

class FakeDBClient(BaseDBClient):
    # It's a temporary mock unless we have access to real DB
    def get_online_orders_counts(self):
        # Imitation reply from DB
        return {"all": 22, "done": 20, "cancel": 2, "active": 0}

    def get_online_orders_from_history_table(self):
        # It's a temporary mock unless we have access to real DB
        return [
            {
                "id": 49105259,
                "name": "49105259",
                "price": 487.57,
                "totalBonus": 0.0,
                "createdOn": "2025-06-20T00:00:00",
                "orderStatus": "Canceled",
                "status": "Скасовано",
                "statusGroup": "canceled",
                "seller": "Епіцентр К",
                "quantity": 2,
                "type": "Online",
                "deliveryId": 45,
                "goods": [
                    "https://cdn.27.ua/190/93/11/6853393_2.jpeg",
                    "https://cdn.27.ua/190/1a/fb/137979_4.jpeg"
                ]
            },
            {
                "id": 47250679,
                "name": "47250679",
                "price": 2837.0,
                "totalBonus": 0.0,
                "createdOn": "2025-04-15T00:00:00",
                "orderStatus": "Canceled",
                "status": "Скасовано",
                "statusGroup": "canceled",
                "seller": "Епіцентр К",
                "quantity": 3,
                "type": "Online",
                "deliveryId": 45,
                "goods": [
                    "https://cdn.27.ua/190/b0/c3/7844035_1.jpeg",
                    "https://cdn.27.ua/190/9e/e3/6921955_2.jpeg",
                    "https://cdn.27.ua/190/de/09/122377_2.jpeg"
                ]
            }
        ]

