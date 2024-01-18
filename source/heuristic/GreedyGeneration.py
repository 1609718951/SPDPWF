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
        # 完成总时间
        self.time = 0
        # 数据复刻
        self.distance_matrix = self.ins.instance.distance_matrix
        self.station_num = len(self.ins.instance.node_dic)
        self.vehicle_num = self.ins.num_vehicle
        self.node_dic = self.ins.instance.node_dic
        self.vehicle_list: list[Vehicle] = self.ins.vehicle_list
        # 通过当前站点和车辆可用时间保证不冲突
        self.vehicle_location = {}
        self.vehicle_usetime = {} # {vehicle1:[[],[],[]],vehicle2:[[],[]]...} or {vehicle1:time1, vehicle2:time2}

        self.order_list: dict[int, Order] = self.ins.order_dic
        self.task: dict[list[Order]] = {}
        # 需要分配的任务vertex
        self.task_queue = PriorityQueue()
        # 最优解道路[path,path] 最优解的完成时间
        self.solution = [[] for i in range(self.vehicle_num)]

    def solve(self):
        # 创建初始距离,更新，每ge vehicle当前访问其他点的距离
        distance_array = np.full((len(self.vehicle_list), self.station_num), Parameter.UP_max)
        # 存储索引和vertex：{索引：节点}
        delivery_dict: dict[int, Vertex] = {}
        # 设定车辆初始位置及可用时间
        for vehicle in self.vehicle_list:
            self.vehicle_location[vehicle.vehicle_id] = vehicle.location
            self.vehicle_usetime[vehicle.vehicle_id] = vehicle.time
        # 构建全部pick，delivery点队列，将pick点放入队列 -> Vertex
        for i in self.order_list.values():
            pick_node = Vertex(i.order_id, i.demand, i.shelf_life, i.start, i.timeWindow)
            self.task_queue.put([pick_node.time_window.get_latest_time(), pick_node])
            delivery_node = Vertex(i.order_id+self.ins.num_order, -i.demand, i.shelf_life, i.end, i.timeWindow)
            delivery_dict[i.order_id+self.ins.num_order] = delivery_node
        while not self.task_queue.empty():
            current_vertex = self.task_queue.get()[1]
            # 创建初始距离,更新，每ge vehicle当前访问其他点的距离
            distance_array = self.update_distance(distance_array)
            assign_to = self.choose_vehicle(current_vertex, distance_array, delivery_dict)
            if assign_to == -1:
                return False
            self.solution[assign_to].append(current_vertex.id)
        return True

    def choose_vehicle(self, vertex: Vertex, distance_matrix, delivery_dict) -> int:
        """选择时间最短的飞机并更新对应delivery节点时间
        :return 分配的对象"""
        assign_id = 0
        can_assign = False
        # 下一个访问节点
        end = vertex.id
        # i.start 进行切片
        queue = PriorityQueue()
        column_data = distance_matrix[:, end]
        for i in range(self.vehicle_num):
            queue.put((column_data[i], i))
        while not queue.empty():
            vehicle = queue.get()
            # 访问下个点的行驶距离，车编号
            value, index = vehicle[0], vehicle[1]
            start = self.vehicle_location[index]
            travel_time = self.distance_matrix[start][end]
            # 判断时间窗是否满足,如果当前点的分配时间大于右侧时间窗，无法分配进入
            arrive_time = travel_time + self.vehicle_usetime[index]
            earliest_time, latest_time = vertex.time_window.get_earliest_time(), vertex.time_window.get_latest_time()
            if arrive_time > latest_time:
                if queue.empty():
                    return -1
                else:
                    continue
            else:
                self.vehicle_location[index] = vertex.position
                if arrive_time < earliest_time:
                    self.vehicle_usetime[index] = earliest_time
                else:
                    self.vehicle_usetime[index] = arrive_time
                # 如果是pick点，解锁对应的delivery点
                if vertex.id < self.ins.num_order:
                    delivery_node = delivery_dict[vertex.id + self.ins.num_order]
                    self.task_queue.put([delivery_node.time_window.get_latest_time(), delivery_node])
                assign_id = index
                self.time += travel_time
                break
        return assign_id

    def update_distance(self, distance_array):
        """更新vehicle位置和其他节点的距离"""
        for i in range(self.ins.num_vehicle):
            for j in range(self.station_num):
                dis_of_vehicle = self.vehicle_list[i].location
                distance_array[i][j] = self.distance_matrix[dis_of_vehicle][j]
        return distance_array

    def get_solution(self):
        """获取解的路径"""
        return self.solution, self.time


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    ins1 = Spdp(file_name)
    ins = SpdpExtension(ins1)
    test = GG(ins)
    test.solve()
    print(test.get_solution())

