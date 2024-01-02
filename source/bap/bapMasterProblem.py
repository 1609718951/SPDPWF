# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/27 09:56
# @Author : Pan Wuhao
from source.model.spdpExtension import SpdpExtension
from gurobipy import *
from source.model.spdpInstance import Spdp
from source.model.path import Path


class BapMasterProblem:
    def __init__(self, instance: SpdpExtension):
        self.ins = instance
        self.num_order = instance.num_order
        self.num_vehicle = instance.num_vehicle
        self.num_station = instance.num_station
        self.num_vertex = instance.num_vertex
        self.vertex_dic = instance.vertex_dic
        self.arc = instance.arc_set
        self.distance = instance.new_distance
        self.constrains = {}
        self.path = {}
        self.construct_model()

    def initial_model(self):
        """设置初始范围"""
        self.model = Model("MP")
        # constrain1 (每个pd点被访问一次)
        for i in range(self.num_vehicle+1, 1 + self.num_vehicle + 2 * self.num_order):
            expr = LinExpr()
            name = "cons1_{}".format(i)
            self.constrains[name] = self.model.addRange(expr, 1, 1, name=name)

        # constrain2 (每辆车被访问一次)
        for i in range(1, self.num_vehicle + 1):
            expr = LinExpr()
            name = "cons2_{}".format(i)
            self.constrains[name] = self.model.addRange(expr, 1, 1, name=name)

        # constrain3 (前后时间约束)
        for i in range(0, self.num_vertex-1):
            for j in range(1, self.num_vertex):
                if (i, j) in self.arc:
                    expr = LinExpr()
                    name = "cons3_{}_{}".format(i, j)
                    self.constrains[name] = self.model.addRange(expr, 0, 0, name=name)

        # constrain4 (同一订单时间前后符合)
        for i in range(1 + self.num_vehicle+2*self.num_order, self.num_vehicle + 3*self.num_order + 1):
            expr = LinExpr()
            # TODO: 右端时间为服务时间
            name = "cons4_{}".format(i)
            self.constrains[name] = self.model.addConstr(expr >= 40, name=name)

        # constrain5 (时间窗约束)
        for i in range(1, self.num_vertex - 1):
            expr = LinExpr()
            name = "cons5_{}".format(i)
            self.constrains[name] = self.model.addRange(expr, self.vertex_dic[i].time_window.get_earliest_time(),
                                                        self.vertex_dic[i].time_window.get_latest_time(), name=name)

    def add_t(self):
        """增加时间窗"""
        for node in range(self.num_vertex):
            coefficients = []
            constr = []
            # 约束3
            for i in range(self.num_vertex):
                for j in range(1, self.num_vertex):
                    if (i, j) in self.arc:
                        name = "cons3_{}_{}".format(i, j)
                        if node == i:
                            coefficients.append(-1)
                            constr.append(self.constrains[name])
                        if node == j:
                            coefficients.append(1)
                            constr.append(self.constrains[name])
            # 约束4
            for i in range(1 + self.num_vehicle+2*self.num_order, self.num_vehicle + 3*self.num_order + 1):
                # TODO: 右端时间为服务时间
                name = "cons4_{}".format(i)
                if node == i:
                    coefficients.append(-1)
                    constr.append(self.constrains[name])
                if node == i+self.num_order:
                    coefficients.append(1)
                    constr.append(self.constrains[name])
            # 约束5
            for i in range(1, self.num_vertex - 1):
                if i == node:
                    name = "cons5_{}".format(i)
                    coefficients.append(1)
                    constr.append(self.constrains[name])

            col = Column(coefficients, constr)
            self.model.addVar(obj=0, vtype=GRB.CONTINUOUS, column=col, name="t_{}".format(node))
        self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=0, name="t_0")

    def add_column(self, path):
        """将可行路加入列"""
        coefficients = []
        constr = []
        dic = {}
        # 约束1，每个pd被访问一次
        for i in range(1+self.num_vehicle, 1+self.num_vehicle+2*self.num_order):
            name = "cons1_{}".format(i)
            dic[name] = path.is_visited_vertex(i)
            coefficients.append(path.is_visited_vertex(i))
            constr.append(self.constrains[name])

        # 约束2，每个k被访问一次
        for i in range(1, self.num_vehicle+1):
            name = "cons2_{}".format(i)
            dic[name] = path.is_visited_vertex(i)
            coefficients.append(path.is_visited_vertex(i))
            constr.append(self.constrains[name])

        # 约束3，每个点时间更新
        for i in range(0, self.num_vertex-1):
            for j in range(1, self.num_vertex):
                if (i, j) in self.arc:
                    name = "cons3_{}_{}".format(i, j)
                    travel_time = self.distance[i][j]
                    coefficients.append(path.is_visited_arc((i, j))*travel_time)
                    print(path.is_visited_arc((i, j)))
                    print(i, j, travel_time, path.is_visited_arc((i, j)))
                    dic[name] = path.is_visited_vertex(i)
                    constr.append(self.constrains[name])

        col = Column(coefficients, constr)
        print(constr)
        print(coefficients)
        self.model.addVar(obj=path.cost, vtype=GRB.BINARY, column=col, name="p_{}".format(path.id))
        self.model.write("test2.lp")
        print(dic)

    def add_path(self):
        """增加可行路"""
        pass

    def construct_model(self):
        self.initial_model()
        self.add_t()

    def solve(self):
        self.model.write("test.lp")
        self.model.optimize()


if __name__ == "__main__":
    file_name = "source/exp/test/2-2-2-0.txt"
    ins = SpdpExtension(Spdp(file_name))
    print(ins.arc_set)
    test = BapMasterProblem(ins)
    print("_", test.distance)
    test.solve()
    path1 = [0, 1, 3, 7, 9, 5, 11]
    path2 = [0, 2, 4, 8, 10, 6, 11]
    p = Path(path1, 100, 0)
    print("+++++++", p.is_visited_arc((7, 9)))
    p2 = Path(path2, 50, 1)
    test.add_column(p)
    test.add_column(p2)
    test.solve()

    # for i in test.vertex_dic.values():
    #     print(i.time_window)ee
