class TimeWindow:
    def __init__(self, ear_time, lat_time):
        self.ear_time: int = ear_time
        self.lat_time: int = lat_time

    def get_earliest_time(self):
        return self.ear_time

    def get_latest_time(self):
        return self.lat_time

    def __str__(self):
        return "[{}:{}]".format(self.ear_time, self.lat_time)
