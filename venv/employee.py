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
    employeeID = data.get("employeeID")
    name = data.get("name")
    address = data.get("address")
    branch = data.get("branch")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_employee_to_neo4j, employeeID, name, address, branch)

    return f"Employee {employeeID} added to Neo4j"

def add_employee_to_neo4j(tx, employeeID, name, address, branch):
    query = (
        "CREATE (e:Employee {employeeID: $employeeID, name: $name, address: $address, branch: $branch})"
    )
    tx.run(query, employeeID=employeeID, name=name, address=address, branch=branch)

@app.route('/get_employee/<employeeID>', methods=['GET'])
def get_employee(employeeID):
    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_employee_from_neo4j, employeeID)

    if result:
        employee_data = {
            "employeeID": employeeID,
            "name": result["name"],
            "address": result["address"],
            "branch": result["branch"]
        }
        return jsonify(employee_data)
    else:
        return jsonify({"message": "Employee not found"}, 404)

def get_employee_from_neo4j(tx, employeeID):
    query = (
        "MATCH (e:Employee {employeeID: $employeeID}) RETURN e"
    )
    result = tx.run(query, employeeID=employeeID).single()
    if result:
        return result["e"]
    else:
        return None

@app.route('/delete_employee/<employeeID>', methods=['DELETE'])
def delete_employee(employeeID):
    with neo4j_driver._driver.session() as session:
        result = session.write_transaction(delete_employee_from_neo4j, employeeID)
    if result:
        return f"Employee {employeeID} has been deleted"
    else:
        return f"Employee {employeeID} not found"

def delete_employee_from_neo4j(tx, employeeID):
    query = (
        "MATCH (e:Employee {employeeID: $employeeID}) DELETE e"
    )
    result = tx.run(query, employeeID=employeeID)
    return result.consume().counters.nodes_deleted

@app.route('/update_employee/<employeeID>', methods=['PUT'])
def update_employee(employeeID):
    data = request.get_json()
    updated_properties = data.get('updated_properties')

    if updated_properties is not None:
        with neo4j_driver._driver.session() as session:
            result = session.read_transaction(get_employee_from_neo4j, employeeID)

            if not result:
                return "Employee not found"

            current_properties = {
                "name": result["name"],
                "address": result["address"],
                "branch": result["branch"]
            }

            for prop, value in updated_properties.items():
                if prop in current_properties:
                    current_properties[prop] = value

            session.write_transaction(update_employee_in_neo4j, employeeID, current_properties)

        return "Employee updated successfully"
    else:
        return "No updated properties provided in the request.", 400

def update_employee_in_neo4j(tx, employeeID, properties):
    query = (
        "MATCH (e:Employee {employeeID: $employeeID}) SET e.name = $name, e.address = $address, e.branch = $branch"
    )
    tx.run(query, employeeID=employeeID, **properties)

if __name__ == '__main__':
    app.run()
