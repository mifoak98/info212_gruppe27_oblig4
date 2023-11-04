from flask import Flask, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

# Set up the Neo4j connection
class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

neo4j_driver = Neo4jDriver("neo4j+s://a0f6f9eb.databases.neo4j.io", "neo4j", "3hCqDbvBlbR_vFBCPgnp1JgwIj_NVyMUwOM6ybNVLsM")

@app.route('/order-car/', methods=['POST'])
def order_car():
    # Get the customerID and carID from the request data
    data = request.get_json()
    customerID = data.get('customerID')
    carID = data.get('carID')

    if not customerID or not carID:
        return jsonify({"message": "Missing customerID or carID"}), 400

    # Use the Neo4j driver to execute the Cypher query
    with neo4j_driver._driver.session() as session:
        result = session.write_transaction(order_car_transaction, customerID, carID)

    if result:
        return jsonify({"message": "Car ordered successfully"}), 200
    else:
        return jsonify({"message": "Car order failed"}), 400

def order_car_transaction(tx, customerID, carID):
    query = (
        f"MATCH (c:Customer {{customerID: '{customerID}', status: 'available'}}), "
        f"(b:Car {{carID: '{carID}', status: 'available'}}) "
        "SET b.status = 'booked' "
        "SET c.status = 'has_booking' "
        "CREATE (c)-[:HAS_BOOKING]->(b) "
    )
    result = tx.run(query)
    return result.summary().counters.nodes_created > 0

if __name__ == '__main__':
    app.run(debug=True)
