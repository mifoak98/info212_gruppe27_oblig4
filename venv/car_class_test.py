

class Cars:
    # Class variable to track the next available car ID
    next_car_id = 1

    def __init__(self, make, model, year, location, status):
        # Automatically generate the car ID and assign it
        self.car_id = Cars.next_car_id
        Cars.next_car_id += 1
        self.make = make
        self.model = model
        self.year = year
        self.location = location
        self.status = status

    def create_car(cls, make, model, year, location, status):
        new_car = cls(make, model, year, location, status)
        return new_car


    def read_car(cls, car_id):
        for car in cars_list:
            if car.car_id == car_id:
                return car
        return None


    def update_car(self, make, model, year, location, status):
        self.make = make
        self.model = model
        self.year = year
        self.location = location
        self.status = status


    def delete_car(cls, car_id):
        # Find the car by ID and remove it from the list
        for car in cars_list:
            if car.car_id == car_id:
                cars_list.remove(car)
                return
