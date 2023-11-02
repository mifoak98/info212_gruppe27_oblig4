from flask import Flask, request, jsonify
from neo4j import GraphDatabase

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_session(self):
        return self._driver.session()

app = Flask(__name__)

neo4j_driver = Neo4jDriver("neo4j://localhost:7687", "neo4j", "password")

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    branch = data.get('branch')

    with neo4j_driver.get_session() as session:
        session.write_transaction(add_employee_to_neo4j, name, address, branch)

    return "Employee added successfully"

def add_employee_to_neo4j(tx, name, address, branch):
    query = (
        "CREATE (e:Employee {name: $name, address: $address, branch: $branch})"
    )
    tx.run(query, name=name, address=address, branch=branch)

@app.route('/get_employee/<name>', methods=['GET'])
def get_employee(name):
    with neo4j_driver.get_session() as session:
        result = session.read_transaction(get_employee_from_neo4j, name)

    if result:
        return jsonify(result)
    else:
        return "Employee not found"

def get_employee_from_neo4j(tx, name):
    query = (
        "MATCH (e:Employee {name: $name}) RETURN e"
    )
    result = tx.run(query, name=name).single()
    if result:
        return result["e"]
    else:
        return None

if __name__ == '__main__':
    app.run()

