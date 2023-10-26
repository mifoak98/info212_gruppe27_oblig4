import json
from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

class Neo4jDriverWrapper:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

neo4j_driver = Neo4jDriverWrapper("neo4j+s://a0f6f9eb.databases.neo4j.io", "neo4j", "3hCqDbvBlbR_vFBCPgnp1JgwIj_NVyMUwOM6ybNVLsM")

class CarDAO:
    def __init__(self, driver):
        self._driver = driver

    def node_to_json(self, node):
        return dict(node.items())

    def find_all_cars(self):
        with self._driver.session() as session:
            cars = session.run("MATCH (a:Car) RETURN a;")
            return [self.node_to_json(record["a"]) for record in cars]

    def find_car_by_reg(self, reg):
        with self._driver.session() as session:
            cars = session.run("MATCH (a:Car{reg:$reg}) RETURN a;", reg=reg)
            return [self.node_to_json(record["a"]) for record in cars]

    def save_car(self, make, model, reg, year, capacity):
        with self._driver.session() as session:
            cars = session.run("MERGE (a:Car{make: $make, model: $model, reg: $reg, year: $year, capacity: $capacity}) RETURN a;", make=make, model=model, reg=reg, year=year, capacity=capacity)
            return [self.node_to_json(record["a"]) for record in cars]

    def update_car(self, make, model, reg, year, capacity):
        with self._driver.session() as session:
            cars = session.run("MATCH (a:Car{reg:$reg}) SET a.make=$make, a.model=$model, a.year=$year, a.capacity=$capacity RETURN a;", reg=reg, make=make, model=model, year=year, capacity=capacity)
            return [self.node_to_json(record["a"]) for record in cars]

    def delete_car(self, reg):
        with self._driver.session() as session:
            session.run("MATCH (a:Car{reg: $reg}) DELETE a;", reg=reg)

car_dao = CarDAO(neo4j_driver._driver)

@app.route('/')
def index():
    with neo4j_driver._driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 25")
        nodes = [record['n']['name'] for record in result]
        
    response_data = {
        "data": nodes,
        "message": "Hello INFO212"
    }
    
    return jsonify(response_data)

@app.route('/get_cars', methods=['GET'])
def get_cars():
    cars = car_dao.find_all_cars()
    return jsonify(cars)

@app.route('/get_cars_by_reg_number', methods=['POST'])
def get_car_by_reg_number():
    data = request.get_json()
    cars = car_dao.find_car_by_reg(data['reg'])
    return jsonify(cars)

@app.route('/save_car', methods=["POST"])
def save_car_info():
    data = request.get_json()
    cars = car_dao.save_car(data['make'], data['model'], data['reg'], data['year'], data['capacity'])
    return jsonify(cars)

@app.route('/update_car', methods=['PUT'])
def update_car_info():
    data = request.get_json()
    cars = car_dao.update_car(data['make'], data['model'], data['reg'], data['year'], data['capacity'])
    return jsonify(cars)

@app.route('/delete_car', methods=['DELETE'])
def delete_car_info():
    data = request.get_json()
    car_dao.delete_car(data['reg'])
    cars = car_dao.find_all_cars()
    return jsonify(cars)

if __name__ == '__main__':
    app.run()
