from source.model.timewindow import TimeWindow


class Order:
    def __init__(self, order_id, start, end, demand, shelf_life, time_window: TimeWindow):
        self.order_id = order_id
        self.start = start
        self.end = end
        self.demand = demand
        self.timeWindow = time_window
        self.shelf_life = shelf_life

    def get_order_id(self):
        return self.order_id

    def get_start_des(self):
        return self.start

    def get_end_des(self):
        return self.end

    def get_demand(self):
        return self.demand

    def get_earliest_time(self):
        return self.timeWindow.get_earliest_time()

    def get_latest_time(self):
        return self.timeWindow.get_latest_time()

    def get_shelf_life(self):
        return self.shelf_life
