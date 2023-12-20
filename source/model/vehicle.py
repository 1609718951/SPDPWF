class Vehicle:
    def __init__(self, vehicle_id, location, speed):
        self.vehicle_id = vehicle_id
        self.location = location
        self.speed = speed

    def get_vehicle_id(self):
        return self.vehicle_id

    def get_location(self):
        return self.location

    def get_speed(self):
        return self.speed


if __name__ == "__main__":
    test = Vehicle(0, 0, 45)
