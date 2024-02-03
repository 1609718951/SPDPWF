# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:31
# @Author : Pan Wuhao
from __future__ import annotations

import string

from source.model.parameter import Parameter
from source.model.spdpExtension import SpdpExtension
from source.model.vertex import Vertex
from source.model.path import Path
from queue import PriorityQueue


class Label:
    def __init__(self, current_node, time, cost, demand, fresh, pre_label: Label, ins:SpdpExtension, distance_matrix):
        """
        :param current_node: 当前节点
        :param cost: 当前cost
        :param demand: 当前容量
        :param fresh: 当前新鲜度字典
        :param pre_label: 父标签
        """
        # 当前代码存在一定的问题，python的内部类使用对比java更为繁琐，可以尝试
        self.order_num = ins.num_order
        self.vehicle_num = ins.num_vehicle
        self.vertex_num = ins.num_vertex
        self.current_node = current_node
        self.distance_matrix = distance_matrix
        self.arc_set = ins.arc_set
        self.vertex_set = ins.vertex_dic
        self.order_set = ins.order_dic
        #
        self.cost = cost
        self.time = time
        self.demand = demand
        self.fresh = fresh
        if pre_label is not None:
            self.pre_label = pre_label
            self.visited_node = pre_label.visited_node.append(current_node)
            # 开始过的点
            self.start_service = pre_label.start_service
            # 需要进行的服务
            self.need_service = pre_label.need_service
            # 已经完成的点
            self.finished_service = self.finished_service
        else:
            self.visited_node = []
            self.start_service = set()
            self.need_service = set()
            self.finished_service = set()
        # 更新已经配送，正在配送，需要配送的订单
        self.update_order_status(current_node)
        self.can_visit_vertex = self.update_can_visit_vertex(current_node)

    def update_can_visit_vertex(self, current_node):
        can_visit_list = set()
        # 初始点，释放所有无人机起点
        if current_node == 0:
            for i in range(1, self.vehicle_num+1):
                can_visit_list.add(i)
                return can_visit_list
        # 无人机点，释放p， sd， e
        if current_node in range(1, self.vehicle_num+1):
            # p
            for i in range(self.vehicle_num+1, self.vehicle_num+self.order_num+1):
                can_visit_list.add(i)
            # sd
            for i in range(self.vehicle_num+1+3*self.order_num, self.vehicle_num+4*self.order_num+2):
                can_visit_list.add(i)
        # 每个点可以访问所有未开始服务的p sd和需要服务的所有d sd
        if current_node in range(1+self.vehicle_num, 1+self.vehicle_num+4*self.order_num):
            # p, 未开始服务以及非当前点可访问
            for i in range(1+self.vehicle_num, 1+self.vehicle_num+self.order_num):
                if  i not in self.start_service:
                    can_visit_list.add(i)
            # sp, 已开始服务且未完成
            for i in range(1+self.vehicle_num+2*self.order_num, 1+self.vehicle_num+3*self.order_num):
                if i-2*self.order_num in self.need_service:
                    can_visit_list.add(i)
            # d, 已开始服务且当前点可访问
            for i in range(1+self.vehicle_num+self.order_num, 1+self.vehicle_num+2*self.order_num):
                if i in self.need_service:
                    can_visit_list.add(i)
            # sd, 未开始服务
            for i in range(1+self.vehicle_num+3*self.order_num, 1+self.vehicle_num+4*self.order_num):
                if i-2*self.order_num not in self.start_service:
                    can_visit_list.add(i)
        # sp, d 在need_service空的情形下可以可以访问e
        if current_node in range(1+self.vehicle_num+self.order_num, 1+self.vehicle_num+3*self.order_num):
            if not self.need_service:
                can_visit_list.add(1+self.vehicle_num+4*self.order_num)
        # 修正 1 无弧不可达 2 超出容量约束 3 超出新鲜度约束 4 超出时间窗约束
        for i in can_visit_list:
            # 1 无弧不可达
            if self.arc_set[current_node, i] is None:
                can_visit_list.remove(i)
                continue
            # 2 超出容量约束
            new_demand = self.vertex_set[i].demand
            if self.demand+new_demand >= 10:
                can_visit_list.remove(i)
                continue
            # 超出新鲜度约束/可无需考虑，在时间窗里进行
            _fresh = self.distance_matrix[current_node, i]*Parameter.cio
            for key, values in self.fresh:
                if values - _fresh < self.order_set[key].shelf_life:
                    can_visit_list.remove(i)
                    continue
            # 4 超出时间窗约束
            if self.distance_matrix[current_node, i] + self.time > self.vertex_set[i].time_window.get_latest_time():
                can_visit_list.remove(i)
        return can_visit_list

    def update_order_status(self, current_node):
        """1.访问p点，服务订单列表中加入开始服务， 加入未访问节点sp"""
        # p 和 sd， 开始服务
        if current_node in range(1+self.vehicle_num, 1+self.vehicle_num+self.order_num):
            self.start_service.add(current_node)
            self.need_service.add(current_node)
        if current_node in range(1+self.vehicle_num+3*self.order_num, 1+self.vehicle_num+4*self.order_num):
            self.start_service.add(current_node-2*self.order_num)
            self.need_service.add(current_node-2*self.order_num)
        # d 和 sp， 结束服务
        if current_node in range(1+self.vehicle_num, 1+self.vehicle_num+self.order_num) :
            self.finished_service.add(current_node)
            self.need_service.remove(current_node)
        if current_node in range(1 + self.vehicle_num + 3 * self.order_num, 1 + self.vehicle_num + 4 * self.order_num):
            self.finished_service.add(current_node - 2 * self.order_num)
            self.need_service.add(current_node - 2 * self.order_num)


class LabelSetting:
    def __init__(self, ins: SpdpExtension):
        self.ins = ins
        self.vertex_num = ins.num_vertex
        self.time_matrix = ins.get_new_cost()
        # 未处理的列表集合
        self.unprocessed_label = PriorityQueue()
        # 全labelList
        self.label_list: list[list[Label]] = [[] for i in range(self.vertex_num)]
        # 全顶点list
        self.vertex_list: list[Vertex] = list(ins.vertex_dic.values())
        # 弧集合
        self.arc_set: dict = ins.arc_set
        self.best_path = None

    def solve(self, lamda):
        print("列生成开始")
        self.reset()
        # 更新新的距离矩阵
        self.update_time_matrix(lamda)
        # 创建初始label
        init_label = Label(0, 0, 0, [], None)
        self.unprocessed_label.put(init_label)
        self.label_list[0].append(init_label)
        while not self.unprocessed_label.empty():
            current_label: Label = self.unprocessed_label.get()
            for i in current_label.can_visit_vertex:
                if self.arc_set[current_label, i]:
                    self.label_extension(current_label, i)
        opt_label = None
        opt = Parameter.UP_max
        for label in self.label_list[-1]:
            if label.cost < opt:
                opt_label = label
                opt = label.cost
        self.best_path = opt_label

    def update_time_matrix(self, lamda):
        pass

    def reset(self):
        # 清空unprocessedList
        length = self.unprocessed_label.qsize()
        while length > 0:
            self.unprocessed_label.get()
            length -= 1
        # 清空labelList
        # TODO:

    def label_extension(self, current_label, node):
        pass

