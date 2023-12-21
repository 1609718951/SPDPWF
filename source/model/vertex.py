# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/13 11:30
# @Author : Pan Wuhao
from source.model.timewindow import TimeWindow


class Vertex:
    def __init__(self, id, demand, fresh, position, time_window=TimeWindow):
        self.id = id
        self.demand = demand
        self.fresh = fresh
        self.position = position
        self.time_window = time_window

    def __str__(self):
        return "ID:{}".format(self.id) + "\tdemand:{}".format(self.demand) + "\tfresh:{}".format(
            self.fresh) + "\ttimewindow:{}".format(self.time_window)


if __name__ == "__main__":
    time = TimeWindow(1, 1)
    test = Vertex(1, 1, 1, time)
    print(test)
