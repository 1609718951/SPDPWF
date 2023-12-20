# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/6 15:20
# @Author : Pan Wuhao
from instance_generate import Instance


class Exp:
    def __init__(self, num_order, num_vehicle, num_node, num_station, times):
        self.num_node = num_node
        self.num_vehicle = num_vehicle
        self.num_order = num_order
        self.num_station = num_station
        self.times = times

    def start(self):
        pass

    def generate_Ins(self):
        this = Instance(self.num_order, self.num_vehicle, self.num_node, self.num_station)
        self.write_to_txt(this)

    def write_to_txt(self, this):
        pass

    def write_solution(self):
        pass

    def solver(self, instance):
        pass
