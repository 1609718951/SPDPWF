from gurobipy import *
from source.model.spdpExtension import SpdpExtension
from source.model.spdpInstance import Spdp


class SpdpGUROBI:
    def __init__(self, instance: SpdpExtension):
        self.instance = instance
        self.num_order = instance.num_order
        self.num_vehicle = instance.num_vehicle
        self.num_station = instance.num_station
        self.num_vertex = instance.num_vertex   # 总的点的数量
        self.order_dic = instance.order_dic
        self.distance_matrix = instance.new_distance
        self.vehicle_list = instance.vehicle_list
        self.vertex_dic = instance.vertex_dic
        self.pick_set = instance.pick_node_set
        self.delivery_set = instance.delivery_node_set
        self.ps_set = instance.p_station_set
        self.sd_set = instance.d_station_set
        self.arc_set = instance.arc_set
        self.x_ijk: GRB.BINARY = {}
        self.C_i = {}
        self.t_i = {}

    def solve(self):
        self.model = Model("SPDP")
        self.add_constrains()
        self.model.optimize()
        self.model.write('SPDP.lp')
        if self.model.status == 2:
            print('model is optimal')
            with open('source/exp/test/{}-{}-{}-{}-solution.txt'.format(self.num_order, self.num_vehicle, self.num_station, 0), 'w') as file:
                for var in self.model.getVars():
                    file.write(f"{var.varName}: {var.x}\n")
        else:
            print(self.model.status)
            self.model.computeIIS()
            if self.model.IISConstr:
                for constr in self.model.getConstrs():
                    if constr.IISConstr:
                        print(f"Constraint Name: {constr.ConstrName}")
            self.model.write('infeasible_.lp')

    def initial_var(self):
        """
        x_{ij}^k: ij在所有顶点中，k在所有车辆中
        :return:
        """
        for i in range(self.num_vertex - 1):
            for j in range(self.num_vertex):
                for k in range(1, self.num_vehicle + 1):
                    if (i, j) in self.arc_set:
                        self.x_ijk[i, j, k] = self.model.addVar(vtype=GRB.BINARY, name="x_{}_{}_{}".format(i, j, k))

        for i in range(self.num_vertex):
            self.C_i[i] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1000000, name="C_{}".format(i))

        for i in range(self.num_vertex):
            self.t_i[i] = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1000000, name="t_{}".format(i))

    def add_constrains(self):
        self.initial_var()
        self.objective()
        self.constrains1()
        self.constrains2()
        self.constrains3()
        self.constrains4()
        # self.test()
        self.constrains5()
        self.constrains5a()

        self.constrains6()
        self.constrains7()
        self.constrains8()
        self.constrains9()
        self.constrains10()
        self.constrains11()
        self.constrains12()

    def test(self):
        self.model.addConstr(1 == self.x_ijk[0, 1, 1])
        self.model.addConstr(1 == self.x_ijk[1, 3, 1])
        self.model.addConstr(1 == self.x_ijk[3, 7, 1])
        self.model.addConstr(1 == self.x_ijk[7, 9, 1])
        self.model.addConstr(1 == self.x_ijk[9, 5, 1])
        self.model.addConstr(1 == self.x_ijk[5, 11, 1])
        self.model.addConstr(1 == self.x_ijk[0, 2, 2])
        self.model.addConstr(1 == self.x_ijk[2, 4, 2])
        self.model.addConstr(1 == self.x_ijk[4, 8, 2])
        self.model.addConstr(1 == self.x_ijk[8, 10, 2])
        self.model.addConstr(1 == self.x_ijk[10, 6, 2])
        self.model.addConstr(1 == self.x_ijk[6, 11, 2])

    def objective(self):
        expr = LinExpr()
        for i in range(self.num_vertex - 1):
            for j in range(1, self.num_vertex):
                for k in range(1, self.num_vehicle + 1):
                    if (i, j) in self.arc_set:
                        expr.addTerms(self.distance_matrix[i][j], self.x_ijk[i, j, k])
        self.model.setObjective(expr)

    # 约束1
    def constrains1(self):
        # \sum_{k' \in K} x_{ok'}^k = 1
        for i in range(1, self.num_vehicle + 1):
            expr = LinExpr()
            for k in range(1, self.num_vehicle + 1):
                expr.addTerms(1, self.x_ijk[0, k, i])
            self.model.addConstr(1 == expr, name="cons1_{}".format(i))

    def constrains2(self):
        # 每个点只访问一次 \sum_k\sum_i x_{ij}^k = 1
        for j in range(1, self.num_vertex - 1):
            expr = LinExpr()
            for k in range(1, self.num_vehicle + 1):
                for i in range(0, self.num_vertex - 1):
                    if (i, j) in self.arc_set:
                        expr.addTerms(1, self.x_ijk[i, j, k])
            self.model.addConstr(1 == expr, name="cons2_{}".format(j))

    def constrains3(self):
        """pp'联合访问"""
        for k in range(1, self.num_vehicle + 1):
            for i in range(1 + self.num_vehicle, 1 + self.num_vehicle + 2 * self.num_order):
                expr = LinExpr()
                expr2 = LinExpr()
                for j in range(1, self.num_vertex - 1):
                    if (j, i) in self.arc_set:
                        expr.addTerms(1, self.x_ijk[j, i, k])
                for l in range(1, self.num_vertex):
                    if (i + 2 * self.num_order, l) in self.arc_set:
                        expr2.addTerms(1, self.x_ijk[i + 2 * self.num_order, l, k])
                self.model.addConstr(expr == expr2, name="cons3_{}".format(i))

    def constrains4(self):
        """流平衡"""
        for k in range(1, self.num_vehicle + 1):
            for j in range(1, self.num_vertex - 1):
                expr = LinExpr()
                expr2 = LinExpr()
                for i in range(self.num_vertex - 1):
                    if (i, j) in self.arc_set:
                        expr.addTerms(1, self.x_ijk[i, j, k])
                for l in range(self.num_vertex):
                    if (j, l) in self.arc_set:
                        expr2.addTerms(1, self.x_ijk[j, l, k])
                self.model.addConstr(expr == expr2, name="cons4_{}_{}".format(j, k))

    def constrains5(self):
        """回到终点k, ps, d"""
        for k in range(1, self.num_vehicle + 1):
            expr = LinExpr()
            # k
            for i in range(1, self.num_vehicle + 1):
                expr.addTerms(1, self.x_ijk[i, self.num_vertex - 1, k])
            # d
            for i in range(self.num_vehicle + 1 + self.num_order, self.num_vehicle + 1 + 2 * self.num_order):
                expr.addTerms(1, self.x_ijk[i, self.num_vertex - 1, k])
            # ps
            for i in range(self.num_vehicle + 1 + 2 * self.num_order, self.num_vehicle + 1 + 3 * self.num_order):
                expr.addTerms(1, self.x_ijk[i, self.num_vertex - 1, k])
            self.model.addConstr(expr == 1, name="cons5_{}".format(k))

    def constrains5a(self):
        # sink约束
        expr = LinExpr()
        for k in range(1, self.num_vehicle + 1):
            for i in range(1, self.num_vertex - 1):
                if (i, self.num_vertex - 1) in self.arc_set:
                    expr.addTerms(1, self.x_ijk[i, self.num_vertex - 1, k])
        self.model.addConstr(expr == self.num_vehicle)

    def constrains6(self):
        """ 容量约束 """
        for k in range(1, self.num_vehicle + 1):
            for i in range(self.num_vertex):
                for j in range(self.num_vertex):
                    if (i, j) in self.arc_set:
                        self.model.addConstr(
                            self.C_i[i] + self.vertex_dic[i].demand <= self.C_i[j] + 100000 * (1 - self.x_ijk[i, j, k]),
                            name="constrain6_{}".format(k))

    def constrains7(self):
        # 容量窗口
        for i in range(1, self.num_vertex - 1):
            self.model.addConstr(0 <= self.C_i[i], name="constrain7")
            self.model.addConstr(self.C_i[i] <= 15, name="constrain7")

    def constrains8(self):
        """时间窗"""
        for k in range(1, self.num_vehicle + 1):
            for i in range(self.num_vertex):
                for j in range(self.num_vertex):
                    if (i, j) in self.arc_set:
                        self.model.addConstr(
                            self.t_i[i] + self.distance_matrix[i][j] <= self.t_i[j] + 10000000 * (
                                        1 - self.x_ijk[i, j, k]), name="constrain8")

    def constrains9(self):
        # 时间窗
        for i in range(1, self.num_vertex - 1):
            self.model.addConstr(self.vertex_dic[i].time_window.get_earliest_time() <= self.t_i[i], name="constrain9")
            self.model.addConstr(self.t_i[i] <= self.vertex_dic[i].time_window.get_latest_time(), name="constrain9")

    def constrains10(self):
        # 服务先后
        for i in range(self.num_vehicle + 1, self.num_vehicle + 1 + self.num_order):
            self.model.addConstr(self.t_i[i] <= self.t_i[i + 2 * self.num_order])

        for i in range(self.num_vehicle + 1 + self.num_order, self.num_vehicle + 1 + 2 * self.num_order):
            self.model.addConstr(self.t_i[i] >= self.t_i[i + 2 * self.num_order])

    def constrains11(self):
        """新鲜度"""
        for i in range(self.num_vehicle + 1, self.num_vehicle + 1 + self.num_order):
            self.model.addConstr(
                self.t_i[i + self.num_order] - self.t_i[i] <= self.order_dic[i - self.num_vehicle - 1].shelf_life * 60)

    def constrains12(self):
        self.model.addConstr(self.C_i[0] == 0)
        self.model.addConstr(self.t_i[0] == 0)


if __name__ == "__main__":
    file_name = "source/exp/test/6-4-4-0.txt"
    test = SpdpExtension(Spdp(file_name))
    test.extension_vertex()
    grb = SpdpGUROBI(test)
    # for i in test.vertex_dic.values():
    #     print(i.time_window)ee
    grb.solve()
