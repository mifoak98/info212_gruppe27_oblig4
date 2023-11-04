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

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    branch = data.get("branch")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_employee_to_neo4j, name, address, branch)

    return "Employee added to Neo4j"

def add_employee_to_neo4j(tx, name, address, branch):
    query = (
        "CREATE (e:Employee {name: $name, address: $address, branch: $branch})"
    )
    tx.run(query, name=name, address=address, branch=branch)

@app.route('/get_employee/<name>', methods=['GET'])
def get_employee(name):
    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_employee_from_neo4j, name)

    if result:
        # Extract node properties and convert to a dictionary
        employee_data = {
            "name": result["name"],
            "address": result["address"],
            "branch": result["branch"]
        }
        return jsonify(employee_data)
    else:
        return jsonify({"message": "Employee not found"}), 404  # Return a 404 Not Found status for no result

def get_employee_from_neo4j(tx, name):
    query = (
        "MATCH (e:Employee {name: $name}) RETURN e"
    )
    result = tx.run(query, name=name).single()
    if result:
        return result["e"]
    else:
        return None

@app.route('/delete_employee/<name>', methods=['DELETE'])
def delete_employee(name):
    with neo4j_driver._driver.session() as session:
        result = session.write_transaction(delete_employee_from_neo4j, name)
    if result:
        return f"Employee {name} has been deleted"
    else:
        return f"Employee {name} not found"

def delete_employee_from_neo4j(tx, name):
    query = (
        "MATCH (e:Employee {name: $name}) DELETE e"
    )
    result = tx.run(query, name=name)
    return result.consume().counters.nodes_deleted

@app.route('/update_employee/<name>', methods=['PUT'])
def update_employee(name):
    data = request.get_json()
    new_address = data.get('address')
    

    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_employee_from_neo4j, name)

        if not result:
            return "Employee not found"

        # Hent eksisterende verdier
        current_name = result["name"]
        current_address = result["address"]
        current_branch = result["branch"]

        # Oppdater kun de feltene som er angitt i JSON-dataen
        if new_address:
            current_address = new_address

        # Oppdater data i Neo4j
        session.write_transaction(update_employee_in_neo4j, current_name, current_address, current_branch)

    return "Employee updated successfully"

def update_employee_in_neo4j(tx, name, address, branch):
    query = (
        "MATCH (e:Employee {name: $name}) SET e.address = $address"
    )
    tx.run(query, name=name, address=address)


@app.route('/add_car', methods=["POST"])
def add_car():
    data = request.get_json()
    carID = data.get("carID")
    car_brand = data.get("car_brand")
    availability = data.get("availability")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_car_to_neo4j, carID, car_brand, availability)

    return "Car added to Neo4j"

def add_car_to_neo4j(tx, carID, car_brand, availability):
    query = (
        "CREATE (e:Car {carID: $carID, car_branc: $car_brand, availability: $availability})"
    )
    tx.run(query, carID=carID, car_brand=car_brand, availability=availability)


if __name__ == '__main__':
    app.run()
