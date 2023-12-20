# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/13 11:30
# @Author : Pan Wuhao
from source.model.timewindow import TimeWindow


class Vertex:
    def __init__(self, id, demand, fresh, time_window = TimeWindow):
        self.id = id
        self.demand = demand
        self.fresh = fresh
        self.time_window = time_window

    def get_id(self):