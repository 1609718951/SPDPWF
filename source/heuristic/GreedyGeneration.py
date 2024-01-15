# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/9 13:36
# @Author : Pan Wuhao
import numpy as np

from source.model.spdpExtension import SpdpExtension,Spdp
from source.model.order import Order
from source.model.parameter import Parameter
from source.model.vehicle import Vehicle
from source.model.vertex import Vertex
from queue import PriorityQueue


class GG:
    def __init__(self, ins: SpdpExtension):
        self.is_solve = False
        self.ins = ins
        self.is_feasible = False
        # 最优解道路[path,path] 最优解的完成时间
        self.solution = []
        self.time = 0
        # 数据复刻
        self.distance_matrix = self.ins.instance.distance_matrix
        self.station_num = len(self.ins.instance.node_dic)
        self.node_dic = self.ins.instance.node_dic
        self.vehicle_list: list[Vehicle] = self.ins.vehicle_list
        self.order_list: dict[int, Order] = self.ins.order_dic
        self.task: dict[list[Order]] = {}
        self.task_queue = PriorityQueue()

    def solve(self):
        # 创建初始距离,更新，每ge vehicle当前访问其他点的距离
        distance_array = np.full((len(self.vehicle_list), self.station_num), Parameter.UP_max)
        distance_array = self.update_distance(distance_array)
        delivery_dict: dict[int, Vertex] = {}
        # 构建全部pick，delivery点队列，将pick点放入队列 -> Vertex
        for i in self.order_list.values():
            pick_node = Vertex(i.order_id, i.demand, i.shelf_life, i.start, i.timeWindow)
            self.task_queue.put([pick_node.time_window.get_latest_time(), pick_node])
            delivery_node = Vertex(i.order_id+self.ins.num_order, -i.demand, i.shelf_life, i.end, i.timeWindow)
            delivery_dict.get(i.order_id+self.ins.num_order, delivery_node)
        # 访问pick点，解锁delivery点
        while self.task_queue.empty():
            current_vertex = self.task_queue.get()
            print(current_vertex)
            #
            if current_vertex.id < self.ins.num_order:
                delivery_node = delivery_dict[current_vertex.id+self.ins.num_order]
                self.task_queue.put([delivery_node.time_window.get_latest_time(), delivery_node])
            start, end = i.start, i.end
            # i.start 进行切片
            column_data = distance_array[:, start]
            print(distance_array)
            min_row_index = np.argmin(column_data)
            print(min_row_index)
            vehicle = self.vehicle_list[min_row_index]
            travel_time = self.distance_matrix[start][end]/vehicle.speed
            vehicle.change_use_time(travel_time)
            vehicle.change_loc(min_row_index)
            self.update_distance(distance_array)
            print(distance_array)

    def assign(self, order: Order, vehicle: Vehicle):
        """基于订单时间窗和车辆时间窗分配"""
        start, end = order.start, order.end
        pass

    def update_distance(self, distance_array):
        for i in range(self.ins.num_vehicle):
            for j in range(self.station_num):
                dis_of_vehicle = self.vehicle_list[i].location
                distance_array[i][j] = self.distance_matrix[dis_of_vehicle][j]
        return distance_array

    def get_solution(self):
        """获取解的路径"""
        return self.solution


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    ins1 = Spdp(file_name)
    ins = SpdpExtension(ins1)
    test = GG(ins)
    test.solve()
