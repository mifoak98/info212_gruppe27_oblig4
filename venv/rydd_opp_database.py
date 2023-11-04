from neo4j import GraphDatabase

# Opprett en Neo4jDriver-klasse for tilkoblingen
class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def run_query(self, query):
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(query))

# Opprett en Neo4jDriver-instans med dine påloggingsopplysninger
neo4j_driver = Neo4jDriver("neo4j+s://a0f6f9eb.databases.neo4j.io", "neo4j", "3hCqDbvBlbR_vFBCPgnp1JgwIj_NVyMUwOM6ybNVLsM")

# Slett noder med standardverdier
query = """
MATCH (c:Customer)
WHERE c.customerID = "default_customerID" AND c.name = "default_name" AND c.address = "default_address" AND c.status = "default_status"
DETACH DELETE c

WITH 1 as dummy

MATCH (car:Car)
WHERE car.carID = "default_carID" AND car.make = "default_make" AND car.model = "default_model" AND car.year = "default_year" AND car.status = "default_status"
DETACH DELETE car
"""

neo4j_driver.run_query(query)

# Lukk tilkoblingen når du er ferdig
neo4j_driver.close()
