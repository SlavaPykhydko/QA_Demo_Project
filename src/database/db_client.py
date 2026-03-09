from sqlalchemy import create_engine, text, URL
from src.common.config import config

class BaseDBClient:
    def get_online_orders_counts(self):
        # This method MUST be overridden in subclasses.
        raise NotImplementedError("The method must be implemented in subclasses")

class DBClient(BaseDBClient):
    def __init__(self):
        # Creating a connection URL via object (when there are all parameters)
        self.connection_url = URL.create(
            drivername="postgresql",  # or "mssql+pyodbc", "mysql+pymysql" etc
            username=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME
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
        return {"all": 21, "done": 19, "cancel": 2}

# Unless we have access to real DB, importing Fake DB client
db_client = FakeDBClient()