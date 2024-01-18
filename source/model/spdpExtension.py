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
    """
    ins:
    2 order 2 vehicle
    0,11 origin and sink
    1,2 vehicle
    3,4 pick
    5,6 delivery
    7,8 pick station
    9,10 delivery station
    """
    def __init__(self, spdp: Spdp):
        """
        :param spdp:
        """
        self.instance = spdp
        self.num_order = spdp.num_order
        self.num_station = spdp.num_station
        self.num_vehicle = spdp.num_vehicle
        # 总的点数，（1开始，range右侧可直接填入）
        self.num_vertex = self.num_vehicle + 4 * self.num_order + 2
        self.physical_distance = spdp.distance_matrix
        self.order_dic = spdp.order_dic
        self.vehicle_list: list[Vehicle] = spdp.vehicle_list
        # 生成节点集合
        # 全节点字典
        self.vertex_dic: dict[int, Vertex] = {}
        # 余下节点
        self.vehicle_dic: dict[int, Vertex] = {}
        self.pick_node_set: dict[int, Vertex] = {}
        self.delivery_node_set: dict[int, Vertex] = {}
        # pick后站点
        self.p_station_set: dict[int, Vertex] = {}
        # delivery后站点
        self.d_station_set: dict[int, Vertex] = {}
        self.new_distance = []
        self.new_cost = []
        self.arc_set = {}
        self.extension()

    def extension(self):
        self.extension_vertex()
        self.calculate_distance()
        self.use_arc_set()

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
        con = 1000
        self.new_distance = np.full((self.num_vertex, self.num_vertex), con)
        # 0 -- k
        for i in self.vehicle_dic.values():
            index = i.id
            self.new_distance[0][index] = 0

        # k -- p sd e
        for i in self.vehicle_dic.values():
            index = i.id
            for j in range(self.num_vehicle+1, self.num_vehicle+self.num_order+1):
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
        # config
        # d无法访问对应sd，p，sd
        for i in range(self.num_vehicle+self.num_order+1, self.num_vehicle+2*self.num_order+1):
            self.new_distance[i][i+2*self.num_order] = con
            self.new_distance[i][i-self.num_order] = con
            self.new_distance[i][i+self.num_order] = con
        # sp无法访问对应p，d，p无法访问d，sd, sd无法访问 p， sp
        for i in range(self.num_vehicle+1, self.num_vehicle+self.num_order+1):
            self.new_distance[i+2*self.num_order][i] = con
            self.new_distance[i+2*self.num_order][i+self.num_order] = con
            self.new_distance[i][i+self.num_order] = con
            self.new_distance[i][i+3*self.num_order] = con
            self.new_distance[i + 3 * self.num_order][i] = con
            self.new_distance[i + 3 * self.num_order][i+2*self.num_order] = con
            # p 无法访问终点
            self.new_distance[i][self.num_vertex-1] = con
        for i in range(self.num_vertex):
            for j in range(self.num_vertex):
                if i == j:
                    self.new_distance[i][j] = con
        self.new_cost = self.new_distance

    def use_arc_set(self):
        for i in range(self.num_vertex):
            for j in range(self.num_vertex):
                if self.new_distance[i][j] < 1000:
                    self.arc_set[i, j] = self.new_distance[i][j]

    def get_new_cost(self):
        return self.new_cost

    def get_num_vertex(self):
        return self.num_vertex


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    test = SpdpExtension(Spdp(file_name))
    test.extension_vertex()
    print(test.vertex_dic)
    print(test.new_distance)
    print(test.arc_set)
