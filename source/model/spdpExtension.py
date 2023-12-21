# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/13 11:30
# @Author : Pan Wuhao
from source.model.spdpInstance import Spdp
from source.model.vertex import Vertex
from source.model.timewindow import TimeWindow
from source.model.vehicle import Vehicle
import numpy as np


class SpdpExtension:
    def __init__(self, spdp: Spdp):
        """
        :param spdp:
        """
        self.instance = spdp
        self.num_order = spdp.num_order
        self.num_station = spdp.num_station
        self.num_vehicle = spdp.num_vehicle
        self.num_vertex = self.num_vehicle + 4 * self.num_order + 2
        self.physical_distance = spdp.distance_matrix
        self.order_dic = spdp.order_dic
        self.vehicle_list: list[Vehicle] = spdp.vehicle_list
        ### 生成节点集合
        self.vertex_dic: dict[int, Vertex] = {}
        self.vehicle_dic: dict[int, Vertex] = {}
        self.pick_node_set: dict[int, Vertex] = {}
        self.delivery_node_set: dict[int, Vertex] = {}
        # pick后站点
        self.p_station_set: dict[int, Vertex] = {}
        # delivery后站点
        self.d_station_set: dict[int, Vertex] = {}
        self.new_distance = []
        self.new_cost = []
        self.extension()

    def extension(self):
        self.extension_vertex()
        self.calculate_distance()

    def extension_vertex(self):
        # 初始节点
        time = TimeWindow(0, 7200)
        self.vertex_dic[0] = Vertex(0, 0, 0, 0, time)
        for i in self.vehicle_list:
            self.vehicle_dic[i.vehicle_id+1] = Vertex(i.vehicle_id+1, 0, 0, i.location, TimeWindow(0, 7200))
            self.vertex_dic[i.vehicle_id+1] = Vertex(i.vehicle_id+1, 0, 0, i.location, TimeWindow(0, 7200))
        for key, value in self.order_dic.items():
            self.pick_node_set[self.num_vehicle + key + 1] = Vertex(self.num_vehicle + key + 1, value.demand,
                                                                    value.shelf_life, value.start, value.timeWindow)
            self.delivery_node_set[self.num_vehicle + key + self.num_order + 1] = Vertex(
                self.num_vehicle + key + self.num_order + 1, -value.demand, value.shelf_life, value.end,
                value.timeWindow)
            self.p_station_set[self.num_vehicle + key + 2 * self.num_order + 1] = Vertex(
                self.num_vehicle + key + 2 * self.num_order + 1, -value.demand, value.shelf_life, value.start,
                value.timeWindow)
            self.d_station_set[self.num_vehicle + key + 3 * self.num_order + 1] = Vertex(
                self.num_vehicle + key + 3 * self.num_order + 1, value.demand, value.shelf_life, value.start,
                value.timeWindow)
        self.vertex_dic.update(self.pick_node_set)
        self.vertex_dic.update(self.delivery_node_set)
        self.vertex_dic.update(self.p_station_set)
        self.vertex_dic.update(self.d_station_set)
        # 虚拟终止节点
        self.vertex_dic[self.num_vertex-1] = Vertex(0, 0, 0, 0, TimeWindow(0, 7200))

    def calculate_distance(self):
        self.new_distance = np.full((self.num_vertex, self.num_vertex), 1000)
        print(self.vertex_dic, self.num_vertex)
        # 0 -- k
        for i in self.vehicle_dic.values():
            index = i.id
            self.new_distance[0][index] = 0

        # k -- others except PS
        for i in self.vehicle_dic.values():
            index = i.id
            for j in range(self.num_vehicle+1, self.num_vehicle+2*self.num_order+1):
                pos1 = i.position
                pos2 = self.vertex_dic[j].position
                self.new_distance[index][j] = self.physical_distance[pos1][pos2]
            for j in range(self.num_vehicle+1+3*self.num_order, self.num_vehicle+4*self.num_order+1):
                pos1 = i.position
                pos2 = self.vertex_dic[j].position
                self.new_distance[index][j] = self.physical_distance[pos1][pos2]
            self.new_distance[index][self.num_vertex-1] = 0

        for i in range(self.num_vehicle+1, self.num_vertex-1):
            for j in range(self.num_vehicle+1, self.num_vertex-1):
                pos1 = self.vertex_dic[i-1].position
                pos2 = self.vertex_dic[j-1].position
                self.new_distance[i][j] = self.physical_distance[pos1][pos2]
            if i <= self.num_vehicle+3*self.num_order:
                self.new_distance[i][self.num_vertex-1] = 0
        self.new_cost = self.new_distance


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    test = SpdpExtension(Spdp(file_name))
    test.extension_vertex()
    print(test.vertex_dic)
    print(test.new_distance)
