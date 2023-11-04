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

@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.get_json()
    carID = data.get("carID")  # Legg til carID fra JSON-payload
    make = data.get("make")
    model = data.get("model")
    year = data.get("year")
    status = data.get("status")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(add_car_to_neo4j, carID, make, model, year, status)

    return "Car added to Neo4j"

def add_car_to_neo4j(tx, carID, make, model, year, status):
    query = (
        "CREATE (c:Car {carID: $carID, make: $make, model: $model, year: $year, status: $status})"
    )
    tx.run(query, carID=carID, make=make, model=model, year=year, status=status)

@app.route('/get_car/<carID>', methods=['GET'])
def get_car(carID):
    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_car_from_neo4j, carID)

    if result:
        car_data = {
            "carID": carID,
            "make": result["make"],
            "model": result["model"],
            "year": result["year"],
            "status": result["status"]
        }
        return jsonify(car_data)
    else:
        return jsonify({"message": "Car not found"}, 404)

def get_car_from_neo4j(tx, carID):
    query = (
        "MATCH (c:Car {carID: $carID}) RETURN c"
    )
    result = tx.run(query, carID=carID).single()
    if result:
        return result["c"]
    else:
        return None

@app.route('/delete_car/<carID>', methods=['DELETE'])
def delete_car(carID):
    with neo4j_driver._driver.session() as session:
        result = session.write_transaction(delete_car_from_neo4j, carID)
    if result:
        return f"Car {carID} has been deleted"
    else:
        return f"Car {carID} not found"

def delete_car_from_neo4j(tx, carID):
    query = (
        "MATCH (c:Car {carID: $carID}) DELETE c"
    )
    result = tx.run(query, carID=carID)
    return result.consume().counters.nodes_deleted


@app.route('/update_car/<carID>', methods=['PUT'])
def update_car(carID):
    data = request.get_json()
    updated_properties = data.get('updated_properties')

    with neo4j_driver._driver.session() as session:
        result = session.read_transaction(get_car_from_neo4j, carID)

        if not result:
            return "Car not found"

        current_properties = {
            "make": result["make"],
            "model": result["model"],
            "year": result["year"],
            "status": result["status"]
        }

        for prop, value in updated_properties.items():
            if prop in current_properties:
                current_properties[prop] = value

        session.write_transaction(update_car_in_neo4j, carID, current_properties)

    return "Car updated successfully"

def update_car_in_neo4j(tx, carID, properties):
    query = (
        "MATCH (c:Car {carID: $carID}) SET c.make = $make, c.model = $model, c.year = $year, c.status = $status"
    )
    tx.run(query, carID=carID, **properties)

if __name__ == '__main__':
    app.run()
