# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/13 11:30
# @Author : Pan Wuhao
from source.model.spdpInstance import Spdp
from source.model.vertex import Vertex

class SpdpExtension:
    def __init__(self, spdp: Spdp):
        self.instance = spdp
        self.num_order = spdp.num_order
        self.num_station = spdp.num_station
        self.num_vehicle = spdp.num_vehicle
        self.mum_node = spdp.num_node
        self.physical_distance = spdp.distance_matrix
        ### 生成节点集合
        self.vertex_set = {}
        self.pick_node_set = {}
        self.delivery_node_set = {}
        # pick后站点
        self.s_station_set = {}
        # delivery后站点
        self.d_station_set = {}

    def extension_vertex(self):
        # 初始节点
        pass

    def calculate_distance(self):
        pass

