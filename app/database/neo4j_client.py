from neo4j import GraphDatabase
from app.config.settings import settings


class Neo4jClient:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD
            )
        )

        self.database = settings.NEO4J_DATABASE

    def verify_connection(self):
        self.driver.verify_connectivity()
        print("Successfully connected to Neo4j")

    def execute_query(self, query: str, parameters: dict | None = None):
        records, summary, keys = self.driver.execute_query(
            query,
            parameters_=parameters or {},
            database_=self.database
        )
        return records

    def close(self):
        self.driver.close()