# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/12 15:02
# @Author : Pan Wuhao
import math
from source.model.vehicle import Vehicle
from source.model.order import Order
from source.model.timewindow import TimeWindow


class Spdp:
    def __init__(self, filename):
        self.filename = filename
        self.num_order = 0
        self.num_vehicle = 0
        self.num_node = 0
        self.num_station = 0
        self.order_dic = {}
        # 总合计需求点数加车站数个点
        self.node_dic = {}
        self.vehicle_list = []
        self.total_num_node = 0
        self.distance_matrix = []
        self.cal_instance()

    def cal_instance(self):
        self.read_txt()
        self.calculate_distance()

    def read_txt(self):
        with open(self.filename, 'r') as file:
            # 读取整个文件内容
            content = file.readlines()
        base_line = content[0].strip().split("-")
        self.num_order, self.num_station, self.num_vehicle = int(base_line[0]), int(base_line[1]), int(base_line[2])
        start = content.index("-#-station location\n")+1
        end = content.index('-@-vehicle station\n')-1
        for line in content[start: end]:
            part = line.strip().split("\t")
            # 键转为整数，坐标转为列表
            self.node_dic[int(part[0])] = eval(part[1])
        start_vehicle = content.index('-@-vehicle station\n')+1
        end_vehicle = content.index('-$-order\n')-1
        self.total_num_node = end - start
        for line in content[start_vehicle: end_vehicle]:
            part = line.strip().split("\t")
            self.vehicle_list.append(Vehicle(int(part[0]), int(part[1]), 45))

        start_order = content.index('-$-order\n')+2
        for line in content[start_order:]:
            part = line.strip().split("\t")
            time_window = TimeWindow(part[4][0], part[4][1])
            self.order_dic[int(part[0])] = Order(int(part[0]), int(part[1]), int(part[2]), int(part[3]), time_window)

    def calculate_distance(self):
        # 距离
        self.distance_matrix = [[] for i in range(self.total_num_node)]
        for i in range(self.total_num_node):
            for j in range(self.total_num_node):
                node1 = self.node_dic[i]
                node2 = self.node_dic[j]
                distance = math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)
                self.distance_matrix[i].append(distance)


if __name__ == "__main__":
    file_name = "/Users/whp/Desktop/大论文/spdp/source/exp/test/6-2-2-0.tex"
    test = Spdp(file_name)
    print(test.distance_matrix)
