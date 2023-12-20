import math
import random
import numpy as np
from source.model.order import Order
from source.model.timewindow import TimeWindow
from source.model.vehicle import Vehicle


class Instance:
    def __init__(self, num_order, num_vehicle, num_node, num_station):
        self.num_order = num_order
        self.num_vehicle = num_vehicle
        self.num_node = num_node
        self.num_station = num_station
        self.order_dic = {}
        # 总合计需求点数加车站数个点
        self.node_dic = {}
        self.vehicle_list = []
        self.total_num_node = num_node+num_station-1
        self.distance_matrix = [[] for i in range(self.total_num_node)]
        self.generate_instance()

    def generate_instance(self):
        self.generate_order()
        self.generate_node()
        self.generate_station()
        self.generate_vehicle()
        self.calculate_distance()

    def generate_node(self):
        for i in range(self.num_node):
            x = round(random.uniform(0, 20))
            y = round(random.uniform(0, 20))
            self.node_dic[i] = [x, y]

    def generate_order(self):
        for i in range(self.num_order):
            # 生成不重复的随机数
            des_order = random.sample(range(0, self.num_node), 2)
            start = random.randint(self.num_station, self.total_num_node)
            end = random.randint(0, self.num_station)
            demand = format(random.uniform(0, 10), '.2f')
            time = random.randint(0, 200)
            deadline = random.randint(time+1800, 3600)
            time_window = TimeWindow(time, deadline)
            shelf_life = 30
            # self.order_dic[i] = Order(i, des_order[0], des_order[1], demand, time_window)
            self.order_dic[i] = Order(i, start, end, demand, shelf_life, time_window)

    def generate_station(self):
        for i in range(self.num_station):
            x = round(random.uniform(0, 20), 2)
            y = round(random.uniform(0, 20), 2)
            self.node_dic[i+self.num_node-1] = [x, y]

    # 计算点之间的距离
    def calculate_distance(self):
        # 距离
        for i in range(self.total_num_node):
            for j in range(self.total_num_node):
                node1 = self.node_dic[i]
                node2 = self.node_dic[j]
                distance = math.sqrt((node1[0]-node2[0])**2+(node1[1]-node2[1])**2)
                self.distance_matrix[i].append(distance)

    def generate_vehicle(self):
        for i in range(self.num_vehicle):
            location = random.randint(0, self.num_node)
            self.vehicle_list.append(Vehicle(i, location, 45))

    def write_to_txt(self, exp_index):
        file_name = "exp/test/{}-{}-{}-{}.txt".format(self.num_order, self.num_station, self.num_vehicle, exp_index)
        with open(file_name, 'a') as f:
            f.truncate(0)
            f.write("{}-{}-{}-{}\n".format(self.num_order, self.num_station, self.num_vehicle, exp_index))
            f.write("num of order:{} \nnum of station:{} \nnum of vehicle:{}\n\n-#-station location\n".format(self.num_order, self.num_station, self.num_vehicle))

            location_string = []
            location_cor = []
            for i in range(self.num_node):
                location_string.append(i)
                location_cor.append(self.node_dic[i])
            for data, info in zip(location_string, location_cor):
                f.write(f'{data}\t{info}\n')

            f.write("\n-@-vehicle station\n")
            vehicle_index = []
            vehicle_station = []
            for i in self.vehicle_list:
                vehicle_index.append(i.get_vehicle_id())
                vehicle_station.append(i.get_location())
            for data, info in zip(vehicle_index, vehicle_station):
                f.write(f'{data}\t{info}\n')

            f.write("\n-$-order\n订单\t起点\t终点\t重量\t保质期\t时间窗\n")
            for orders, details in self.order_dic.items():
                f.write(f'{orders}\t')
                f.write('{}\t{}\t{}\t{}\t{}\n'.format(details.start, details.end, details.demand, details.shelf_life, [details.timeWindow.get_earliest_time(),details.timeWindow.get_latest_time()]))


if __name__ == "__main__":
    order = 6
    station = 2
    vehicle = 2
    node = 4
    test = Instance(num_order=order, num_vehicle=vehicle, num_node=node, num_station=station)
    test.write_to_txt(0)
