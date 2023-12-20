import gurobipy as gb
from source.model.spdpInstance import Spdp


class SpdpGUROBI:
    def __init__(self, instance: Spdp):
        self.instance = instance
        self.num_order = instance.num_order
        self.num_vehicle = instance.num_vehicle
        self.num_station = instance.num_station
        self.num_vertex = instance.total_num_node

        self.order_dic = instance.order_dic
        self.distance_matrix = instance.distance_matrix
        self.vehicle_list = instance.vehicle_list
        self.node_dic = instance.node_dic

    def solve(self):
        pass

    def initial_var(self):
        pass

    def add_constrains(self):
        self.constrains1()

    # 约束1
    def constrains1(self):
        pass

    def constrains2(self):
        pass

    def constrains3(self):
        pass

    def constrains4(self):
        pass

    def constrains5(self):
        pass

    def constrains6(self):
        pass

    def constrains7(self):
        pass

    def constrains8(self):
        pass

    def constrains9(self):
        pass

    def constrains10(self):
        pass

    def constrains11(self):
        pass

    def constrains12(self):
        pass
