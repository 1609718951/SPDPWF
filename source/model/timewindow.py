class TimeWindow:
    def __init__(self, ear_time, lat_time):
        self.ear_time = ear_time
        self.lat_time = lat_time

    def get_earliest_time(self):
        return self.ear_time

    def get_latest_time(self):
        return self.lat_time
