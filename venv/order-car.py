from flask import Flask, request, jsonify

app = Flask(__name)

# Sample data structures to keep track of customers and cars
customers = {}
cars = {}

@app.route('/order-car', methods=['POST'])
def order_car():
    customer_id = request.json.get('customer_id')
    car_id = request.json.get('car_id')

    if customer_id in customers:
        return jsonify({"message": "Customer already has a booking."}), 400

    if car_id not in cars:
        return jsonify({"message": "Car not found."}), 404

    if cars[car_id]['status'] == 'available':
        cars[car_id]['status'] = 'booked'
        customers[customer_id] = car_id
        return jsonify({"message": "Car booked successfully."})

    return jsonify({"message": "Car is not available for booking."}), 400

@app.route('/cancel-order-car', methods=['POST'])
def cancel_order_car():
    customer_id = request.json.get('customer_id')
    car_id = request.json.get('car_id')

    if customer_id not in customers or customers[customer_id] != car_id:
        return jsonify({"message": "Customer has no booking for this car."}), 400

    cars[car_id]['status'] = 'available'
    del customers[customer_id]
    return jsonify({"message": "Booking canceled successfully."})

@app.route('/rent-car', methods=['POST'])
def rent_car():
    customer_id = request.json.get('customer_id')
    car_id = request.json.get('car_id')

    if customer_id not in customers or customers[customer_id] != car_id:
        return jsonify({"message": "Customer has no booking for this car."}), 400

    if cars[car_id]['status'] == 'booked':
        cars[car_id]['status'] = 'rented'
        return jsonify({"message": "Car rented successfully."})

    return jsonify({"message": "Car is not available for renting."}), 400

@app.route('/return-car', methods=['POST'])
def return_car():
    customer_id = request.json.get('customer_id')
    car_id = request.json.get('car_id')
    car_status = request.json.get('car_status')

    if customer_id not in customers or customers[customer_id] != car_id:
        return jsonify({"message": "Customer has no booking for this car."}), 400

    if cars[car_id]['status'] == 'rented':
        if car_status == 'ok':
            cars[car_id]['status'] = 'available'
        elif car_status == 'damaged':
            cars[car_id]['status'] = 'damaged'
        return jsonify({"message": "Car returned successfully."})

    return jsonify({"message": "Car cannot be returned in this status."}), 400

if __name__ == '__main__':
    app.run(debug=True)