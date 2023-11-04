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

cars = [
    {'id': 1, 'status': 'available'},
    {'id': 2, 'status': 'available'},
    {'id': 3, 'status': 'available'}
]

customers = [
    {'id': 1, 'booking': None},
    {'id': 2, 'booking': None},
    {'id': 3, 'booking': None}
]


@app.route('/')
def index():
    return "Welcome"


def find_car(car_id):
    return next((car for car in cars if car['id'] == car_id), None)

def find_customer(customer_id):
    return next((customer for customer in customers if customer['id'] == customer_id), None)

@app.route('/order-car', methods=['POST'])
def order_car():
    customer_id = request.json['customer_id']
    car_id = request.json['car_id']

    customer = find_customer(customer_id)
    car = find_car(car_id)

    if not customer or not car or car['status'] != 'available':
        return jsonify({'message': 'Invalid order request'}), 400

    car['status'] = 'booked'
    customer['booking'] = car_id

    return jsonify({'message': 'Car ordered successfully'})

@app.route('/cancel-order-car', methods=['POST'])
def cancel_order_car():
    customer_id = request.json['customer_id']
    car_id = request.json['car_id']

    customer = find_customer(customer_id)
    car = find_car(car_id)

    if not customer or not car or car['status'] != 'booked' or customer['booking'] != car_id:
        return jsonify({'message': 'Invalid cancellation request'}),


if __name__ == '__main__':
    app.run()
