import json
from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

neo4j_driver = Neo4jDriver("neo4j+s://a0f6f9eb.databases.neo4j.io", "neo4j", "3hCqDbvBlbR_vFBCPgnp1JgwIj_NVyMUwOM6ybNVLsM")

@app.route('/')
def index():
    return "Welcome"

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()
    customerID = data.get("customerID")
    name = data.get("name")
    address = data.get("address")
    status = data.get("status")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_customer_to_neo4j, customerID, name, address, status)

    return f"Customer {customerID} added to Neo4j"

def add_customer_to_neo4j(tx, customerID, name, address, status):
    query = (
        "CREATE (c:Customer {customerID: $customerID, name: $name, address: $address, status: $status})"
    )
    tx.run(query, customerID=customerID, name=name, address=address, status=status)

@app.route('/get_customer/<customerID>', methods=['GET'])
def get_customer(customerID):
    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_customer_from_neo4j, customerID)

    if result:
        customer_data = {
            "customerID": customerID,
            "name": result["name"],
            "address": result["address"],
            "status": result["status"]
        }
        return jsonify(customer_data)
    else:
        return jsonify({"message": "Customer not found"}), 404  # Return a 404 Not Found status for no result

def get_customer_from_neo4j(tx, customerID):
    query = (
        "MATCH (c:Customer {customerID: $customerID}) RETURN c"
    )
    result = tx.run(query, customerID=customerID).single()
    if result:
        return result["c"]
    else:
        return None

@app.route('/delete_customer/<customerID>', methods=['DELETE'])
def delete_customer(customerID):
    with neo4j_driver._driver.session() as session:
        result = session.write_transaction(delete_customer_from_neo4j, customerID)
    if result:
        return f"Customer {customerID} has been deleted"
    else:
        return f"Customer {customerID} not found"

def delete_customer_from_neo4j(tx, customerID):
    query = (
        "MATCH (c:Customer {customerID: $customerID}) DELETE c"
    )
    result = tx.run(query, customerID=customerID)
    return result.consume().counters.nodes_deleted

@app.route('/update_customer/<customerID>', methods=['PUT'])
def update_customer(customerID):
    data = request.get_json()
    updated_properties = data.get('updated_properties')

    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_customer_from_neo4j, customerID)

        if not result:
            return "Customer not found"

        current_properties = {
            "name": result["name"],
            "address": result["address"],
            "status": result["status"]
        }

        for prop, value in updated_properties.items():
            if prop in current_properties:
                current_properties[prop] = value

        session.write_transaction(update_customer_in_neo4j, customerID, current_properties)

    return "Customer updated successfully"

def update_customer_in_neo4j(tx, customerID, properties):
    query = (
        "MATCH (c:Customer {customerID: $customerID}) SET c.name = $name, c.address = $address, c.status = $status"
    )
    tx.run(query, customerID=customerID, **properties)

if __name__ == '__main__':
    app.run()
