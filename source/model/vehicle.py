class Vehicle:
    def __init__(self, vehicle_id, location, speed):
        self.vehicle_id: int = vehicle_id
        self.location: int = location
        self.speed = speed
        self.time = 0
        self.cap = 10

    def get_vehicle_id(self):
        return self.vehicle_id

    def get_location(self):
        return self.location

    def get_speed(self):
        return self.speed

    def change_loc(self, loc):
        self.location = loc

    def change_use_time(self, time):
        self.time = time

    def pick(self, demand) -> bool:
        """判断是否不可取"""
        if self.cap + demand > 10:
            return False
        else:
            self.cap += demand
            return True

    def delivert(self, demand) -> bool:
        """判断是否不可取"""
        if self.cap - demand > 10:
            return False
        else:
            self.cap -= demand
            return True


if __name__ == "__main__":
    test = Vehicle(0, 0, 45)
