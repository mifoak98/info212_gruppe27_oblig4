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
    name = data.get("name")
    address = data.get("address")
    customerID = data.get("customerID")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_customer_to_neo4j, name, address, customerID)

    return "Customer added to Neo4j"

def add_customer_to_neo4j(tx, name, address, customerID):
    query = (
        "CREATE (c:Customer {name: $name, address: $address, customerID: $customerID})"
    )
    tx.run(query, name=name, address=address, customerID=customerID)

@app.route('/get_customer/<name>', methods=['GET'])
def get_customer(name):
    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_customer_from_neo4j, name)

    if result:
        # Extract node properties and convert to a dictionary
        customer_data = {
            "name": result["name"],
            "address": result["address"],
            "customerID": result["customerID"]
        }
        return jsonify(customer_data)
    else:
        return jsonify({"message": "Customer not found"}), 404  # Return a 404 Not Found status for no result

def get_customer_from_neo4j(tx, name):
    query = (
        "MATCH (c:Customer {name: $name}) RETURN c"
    )
    result = tx.run(query, name=name).single()
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

@app.route('/update_customer/<name>', methods=['PUT'])
def update_customer(name):
    data = request.get_json()
    new_address = data.get('address')

    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_customer_from_neo4j, name)

        if not result:
            return "Customer not found"

        # Hent eksisterende verdier
        current_name = result["name"]
        current_address = result["address"]

        # Oppdater kun de feltene som er angitt i JSON-dataen
        if new_address:
            current_address = new_address

        # Oppdater data i Neo4j
        session.write_transaction(update_customer_in_neo4j, current_name, current_address)

    return "Customer updated successfully"

def update_customer_in_neo4j(tx, name, address):
    query = (
        "MATCH (c:Customer {name: $name}) SET c.address = $address"
    )
    tx.run(query, name=name, address=address)

if __name__ == '__main__':
    app.run()
