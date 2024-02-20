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
from source.model.spdpInstance import Spdp


class Label:
    def __init__(self, current_node, time, cost, demand, fresh, pre_label: Label, ins: SpdpExtension, distance_matrix):
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
        self.ins = ins
        self.time_matrix = distance_matrix
        #
        self.cost = cost
        self.time = time
        self.demand = demand
        self.fresh = fresh
        if pre_label is not None:
            self.pre_label = pre_label
            past = pre_label.visited_node
            past.append(current_node)
            self.visited_node = past
            # 开始过的点
            self.start_service = pre_label.start_service
            # 需要进行的服务
            self.need_service = pre_label.need_service
            # 已经完成的点
            self.finished_service = pre_label.finished_service
            #
            self.visited_num = pre_label.visited_num + 1
        else:
            self.visited_node = [0]
            self.visited_num = 0
            self.start_service = set()
            self.need_service = set()
            self.finished_service = set()
        # 更新已经配送，正在配送，需要配送的订单
        self.update_order_status(current_node)
        self.can_visit_vertex: set = self.update_can_visit_vertex(current_node)

    def update_can_visit_vertex(self, current_node):
        can_visit_list = set()
        # 初始点，释放所有无人机起点
        if current_node == 0:
            for i in range(1, self.vehicle_num + 1):
                can_visit_list.add(i)
            return can_visit_list
        # 无人机点，释放p， sd， e
        if current_node in range(1, self.vehicle_num + 1):
            # p
            for i in range(self.vehicle_num + 1, self.vehicle_num + self.order_num + 1):
                can_visit_list.add(i)
            # sd
            for i in range(self.vehicle_num + 1 + 3 * self.order_num, self.vehicle_num + 4 * self.order_num + 2):
                can_visit_list.add(i)
        # 每个点可以访问所有未开始服务的p sd和需要服务的所有d sd
        if current_node in range(1 + self.vehicle_num, 1 + self.vehicle_num + 4 * self.order_num):
            # p, 未开始服务以及非当前点可访问
            for i in range(1 + self.vehicle_num, 1 + self.vehicle_num + self.order_num):
                if i not in self.start_service:
                    can_visit_list.add(i)
            # sp, 已开始服务且未完成
            for i in range(1 + self.vehicle_num + 2 * self.order_num, 1 + self.vehicle_num + 3 * self.order_num):
                if i - 2 * self.order_num in self.need_service:
                    can_visit_list.add(i)
            # d, 已开始服务且当前点可访问
            for i in range(1 + self.vehicle_num + self.order_num, 1 + self.vehicle_num + 2 * self.order_num):
                if i in self.need_service:
                    can_visit_list.add(i)
            # sd, 未开始服务
            for i in range(1 + self.vehicle_num + 3 * self.order_num, 1 + self.vehicle_num + 4 * self.order_num):
                if i - 2 * self.order_num not in self.start_service:
                    can_visit_list.add(i)
        # sp, d 在need_service空的情形下可以可以访问e
        if current_node in range(1 + self.vehicle_num + self.order_num, 1 + self.vehicle_num + 3 * self.order_num):
            if not self.need_service:
                can_visit_list.add(1 + self.vehicle_num + 4 * self.order_num)
        # 修正 1 无弧不可达 2 超出容量约束 3 超出新鲜度约束 4 超出时间窗约束
        elements_to_remove = []
        for i in can_visit_list:
            # 1 无弧不可达
            if (current_node, i) is self.arc_set:
                elements_to_remove.append(i)
                continue
            # 2 超出容量约束
            new_demand = self.vertex_set[i].demand
            if self.demand + new_demand >= 10:
                elements_to_remove.append(i)
                continue
            # 超出新鲜度约束/可无需考虑，在时间窗里进行
            # 当前访问造成任意新鲜度不满足将标记点为不可访问
            _fresh = self.distance_matrix[current_node, i] * Parameter.cio
            for key, values in self.fresh.items():
                print(self.fresh, "xinxiandu", key)
                print(self.order_set)
                if values - _fresh < self.order_set[key - 1].shelf_life:
                    elements_to_remove.append(i)
                    continue
            # 4 超出时间窗约束
            if self.distance_matrix[current_node, i] + self.time > self.vertex_set[i].time_window.get_latest_time():
                elements_to_remove.append(i)
        print(self.visited_node)
        for element in elements_to_remove:
            can_visit_list.remove(element)
        return can_visit_list

    def update_order_status(self, current_node):
        """1.访问p点，服务订单列表中加入开始服务， 加入未访问节点sp"""
        # p 和 sd， 开始服务
        if current_node in range(1 + self.vehicle_num, 1 + self.vehicle_num + self.order_num):
            self.start_service.add(current_node)
            self.need_service.add(current_node)
        if current_node in range(1 + self.vehicle_num + 3 * self.order_num, 1 + self.vehicle_num + 4 * self.order_num):
            self.start_service.add(current_node - 2 * self.order_num)
            self.need_service.add(current_node - 2 * self.order_num)
        # d 和 sp， 结束服务
        if current_node in range(1 + self.vehicle_num, 1 + self.vehicle_num + self.order_num):
            self.finished_service.add(current_node)
            self.need_service.remove(current_node)
        if current_node in range(1 + self.vehicle_num + 3 * self.order_num, 1 + self.vehicle_num + 4 * self.order_num):
            self.finished_service.add(current_node - 2 * self.order_num)
            self.need_service.add(current_node - 2 * self.order_num)

    def __lt__(self, other):
        return self.cost < other.cost

    def copy(self):
        if self.current_node == 0:
            pre_label = None
        else:
            pre_label = self.pre_label
            print("----", self.pre_label)

        return Label(self.current_node,
                     self.time,
                     self.cost,
                     self.demand,
                     self.fresh,
                     pre_label,
                     self.ins,
                     self.time_matrix)

    def __str__(self):
        return "cost:{} \t time:{} \t path:{}".format(self.cost, self.time, self.visited_node)


class LabelSetting:
    def __init__(self, ins: SpdpExtension):
        self.solution = 0
        self.ins = ins
        self.vertex_num = ins.num_vertex
        self.order_num = ins.num_order
        self.vehicle_num = ins.num_vehicle
        self.time_matrix = ins.get_new_cost()
        self.cost_matrix = self.time_matrix
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
        fresh: dict = {}
        # 创建初始label
        init_label = Label(0, 0, 0, 0, fresh, None, self.ins, self.time_matrix)
        self.unprocessed_label.put(init_label)
        self.label_list[0].append(init_label)
        while not self.unprocessed_label.empty():
            current_label: Label = self.unprocessed_label.get()
            print("#", current_label)
            current_node = current_label.current_node
            for i in current_label.can_visit_vertex:
                if (current_node, i) in self.arc_set:
                    print("test", current_label, current_label.can_visit_vertex, i)
                    self.label_extension(current_label, i)
                    print(current_label)
                    print("队列长度", self.unprocessed_label.qsize())
        opt_label = None
        opt = Parameter.UP_max
        print(self.label_list[-1])
        for label in self.label_list[-1]:
            if label.cost < opt:
                opt_label = label
                opt = label.cost
        self.best_path = opt_label
        self.solution = opt_label.time
        print(self.solution)

    def update_time_matrix(self, lamda):
        """更新cost_matrix"""
        pass

    def reset(self):
        # 清空unprocessedList
        length = self.unprocessed_label.qsize()
        while length > 0:
            self.unprocessed_label.get()
            length -= 1
        # 清空labelList
        self.label_list = [[] for i in range(self.vertex_num)]

    def label_extension(self, label, node):
        current_label = label.copy()
        print(current_label)
        print("test")

        current_node = current_label.current_node
        if (current_node, node) not in self.arc_set:
            return
        # 更新cost；time；demand；fresh
        cost, time, demand = current_label.cost, current_label.time, current_label.demand
        cost += self.cost_matrix[current_node, node]
        time += self.time_matrix[current_node, node]
        demand += self.vertex_list[node].demand
        fresh = current_label.fresh
        new_fresh = self.update_fresh(fresh, current_node, node)
        print(current_label.visited_node, type(current_label.visited_node))
        new_label = Label(node, time, cost, demand, new_fresh, current_label, self.ins, self.time_matrix)
        print("label_extension", node, new_label.visited_node, new_label.can_visit_vertex)
        if self.dominate(new_label):
            self.label_list[node].append(new_label)
            self.unprocessed_label.put(new_label)
        else:
            return

    def update_fresh(self, fresh: dict, current_node, node):
        """在这种场景下，新鲜度本质是一种剪枝的行为：即减去完全服务的类型"""
        # 未开始服务的订单，新鲜度为0(新鲜度做加法）
        if node <= self.vehicle_num:
            return fresh
        # p: 加入新，更新余下
        travel_time = self.time_matrix[current_node, node]
        if node <= self.vehicle_num + self.order_num:
            fresh[node - self.vehicle_num] = 0
            for key in fresh.keys():
                fresh[key] += travel_time
            return fresh
        # sp： 删除订单，更新余下
        if node <= self.vehicle_num + 2 * self.order_num:
            fresh.pop(node - 2 * self.order_num)
            for key in fresh.keys():
                fresh[key] += travel_time
            return fresh
        # sd: 加入最理想新鲜度（直接访问到达）
        if node <= self.vehicle_num + 3 * self.order_num:
            min_travel = self.time_matrix[current_node - 3 * self.order_num, current_node - self.order_num]
            fresh[node - self.order_num - self.vehicle_num] = min_travel
            for key in fresh.keys():
                fresh[key] += travel_time
            return fresh
        # d: 删除订单，更新余下
        if node <= self.vehicle_num + 4 * self.order_num:
            fresh.pop(node)
            for key in fresh.keys():
                fresh[key] += travel_time
            return fresh

    def dominate(self, new_label):
        """占优规则：访问的点一样，或更少，时间更长，"""
        node = new_label.current_node
        label_list = self.label_list[node]
        if len(label_list) == 0:
            return True
        # 时间长，使用容量多，列表cost高，无法占优
        for label in label_list:
            #
            if len(new_label.visited_node) < len(label.visited_node):
                return False
            if new_label.time > label.time and new_label.demand > label.time and new_label.cost > label.cost:
                return False
            # 集合覆盖（不满足前置条件的基础下），占优
            if set(new_label.visited_node).issubset(set(label.visited_node)):
                return True
            else:
                return False


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    test = SpdpExtension(Spdp(file_name))
    print(test.num_vertex)
    test.extension_vertex()
    this_test = LabelSetting(test)
    this_test.solve(0)
