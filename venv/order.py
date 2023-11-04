import json
from flask import Flask, request
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

def log_car_rental(tx, customerID, carID):
    query = (
        "MATCH (c:Customer {customerID: $customerID}) "
        "MATCH (car:Car {carID: $carID}) "
        "MERGE (c)-[:BOOKED]->(car) "
        "SET c.status = 'y', car.status = 'booked'"
    )
    tx.run(query, customerID=customerID, carID=carID)

def check_car_availability(tx, carID):
    query = (
        "MATCH (car:Car {carID: $carID, status: 'available'}) "
        "RETURN car"
    )
    result = tx.run(query, carID=carID).single()
    return result

def update_car_status(tx, carID, status):
    query = (
        "MATCH (c:Car {carID: $carID}) SET c.status = $status"
    )
    tx.run(query, carID=carID, status=status)

def check_existing_booking(tx, customerID, carID):
    query = (
        "MATCH (c:Customer {customerID: $customerID})-[:BOOKED]->(car:Car {carID: $carID}) "
        "RETURN car"
    )
    result = tx.run(query, customerID=f"y{customerID}", carID=carID).single()
    return result

def return_car(tx, customerID, carID, car_status):
    if car_status != "damaged":
        car_status = "available"

    with neo4j_driver._driver.session() as session:
        # Delete the "BOOKED" relationship
        session.write_transaction(delete_booking_relationship, customerID, carID)

        # Update properties
        session.write_transaction(update_car_status_and_reset_id, carID, car_status)
        session.write_transaction(update_customer_status, customerID)

def delete_booking_relationship(tx, customerID, carID):
    delete_query = (
        "MATCH (c:Customer {customerID: $customerID})-[r:BOOKED]->(car:Car {carID: $carID}) "
        "DELETE r"
    )
    tx.run(delete_query, customerID=customerID, carID=carID)

def update_customer_status(tx, customerID):
    update_query = (
        "MATCH (c:Customer {customerID: $customerID}) SET c.status = 'n'"
    )
    tx.run(update_query, customerID=customerID)

def update_car_status_and_reset_id(tx, carID, car_status):
    update_query = (
        "MATCH (car:Car {carID: $carID}) SET car.status = $car_status"
    )
    tx.run(update_query, carID=carID, car_status=car_status)

@app.route('/car-order', methods=['POST'])
def car_order():
    data = request.get_json()
    customerID = data.get("customerID")
    carID = data.get("carID")

    # Check if the customer has already booked the car
    with neo4j_driver._driver.session() as session:
        car_result = session.read_transaction(check_car_availability, carID)

    if car_result:
        if car_result["car"]["status"] == "available":
            # Check if the customer has already booked the car
            with neo4j_driver._driver.session() as session:
                existing_booking = session.read_transaction(check_existing_booking, customerID, carID)

            if existing_booking:
                print(f"Car {carID} is already booked by customer {customerID}")
                return "Car is already booked by the same customer", 400
            else:
                # Change the car's status to 'booked'
                with neo4j_driver._driver.session() as session:
                    session.write_transaction(update_car_status, carID, "booked")

                # Log the car rental
                with neo4j_driver._driver.session() as session:
                    session.write_transaction(log_car_rental, customerID, carID)

                return f"Car with ID {carID} has been booked by customer {customerID}"
        else:
            print(f"Car {carID} status: {car_result['car']['status']}")
            return "Car is already booked or not available", 400
    else:
        print(f"Car {carID} not found in the database")
        return "Car not found", 404


@app.route('/car-return', methods=['POST'])
def car_return():
    data = request.get_json()
    customerID = data.get("customerID")
    carID = data.get("carID")
    car_status = data.get("car_status")

    with neo4j_driver._driver.session() as session:
        session.write_transaction(return_car, customerID, carID, car_status)

    return f"Car with ID {carID} has been returned by customer {customerID}"

if __name__ == '__main__':
    app.run(debug=True)
