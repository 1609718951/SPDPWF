# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:39
# @Author : Pan Wuhao
from __future__ import annotations

import copy

from source.model.spdpExtension import SpdpExtension
from source.bap.bapMasterProblem import BapMasterProblem
from source.bap.PriceProblem import PriceProblem
from source.model.arc import Arc
from source.model.parameter import Parameter


class BranchArc(Arc):
    def __init__(self, from_vertex, to_vertex, value):
        super().__init__(from_vertex, to_vertex)
        self.value = value

    def get_value(self):
        return self.value


class BapNode:
    def __init__(self, parent, from_vertex=int, to_vertex=int, branch_value=int, ins=SpdpExtension):
        self.ins = ins
        if BapNode is not None:
            self.parent: BapNode = parent
            self.infeasible_path_list = parent.infeasible_path_list
            self.to_vertex = to_vertex
            self.from_vertex = from_vertex
            self.branch_from_parent = BranchArc(from_vertex, to_vertex, branch_value)
            if branch_value == 0:
                self.node_num = 2*parent.node_num+1
            else:
                self.node_num = 2*parent.node_num+2
        else:
            self.infeasible_path_list = []
            self.branch_from_parent = None
            self.node_num = 0
        self.iterations = 0
        # 每条路的变量值集合
        self.solution = []
        self.is_inter_solution = False
        self.isLP_feasible = True
        # 需要进行分支的弧
        self.arc_to_branch: Arc = None
        self.node_LPobj = None

    def column_generation(self, mp: BapMasterProblem, sp: PriceProblem):
        # 更新当前节点主子问题
        self.update_infeasible_path_set(mp)
        # 更新timemap
        history_branch_arcs: list[BranchArc] = self.get_history_branch()
        # 基于历史访问的弧的value进行全新的distance_matrix更新
        revise_new_time_matrix = self.revise_time_matrix(history_branch_arcs)
        sp.update_time_matrix(revise_new_time_matrix)
        # 每个节点的主问题生成一次初始节点，节点已经生成，则不再生成，无法生成则直接进行子问题求解
        while True:
            self.iterations += 1
            if not mp.solve():
                if self.iterations < 2:
                    initial_paths = mp.generate_initial_paths()
                    if initial_paths is None:
                        self.isLP_feasible = False
                        print("The heuristic failed to find a initial solution")
                        return
                    for path in initial_paths:
                        index = mp.index_of_path(path)
                        if index != -1:
                            mp.add_column(path)
                    continue
                else:
                    self.isLP_feasible = False
                    return
        # 求解子问题
        sp.solve(mp.get_Dual())
        reduce_cost = sp.reduce_cost
        # reduce_cost > 0, 当前解为最优解
        if reduce_cost > Parameter.EPS:
            self.node_LPobj = mp.get_objective()
            self.arc_to_branch = mp.find_arc_to_branch()
            # 整数解
            if self.arc_to_branch is None:
                self.is_inter_solution = True
                use_paths = mp.get_value()
                for i in range(len(use_paths)):
                    if use_paths[i] > 1-Parameter.EPS:
                        self.solution.append(i)
                return
        mp.add_column(sp.get_shortest_path())

    def update_infeasible_path_set(self, mp):
        # root节点返回
        if self.parent is None:
            return
        paths = mp.paths
        if self.branch_from_parent == 0:
            for path in paths:
                if path in self.infeasible_path_list:
                    continue
                visited_vertex = list(path.visited_vertex.keys())
                # 如果访问了弧，path加入到不可行路
                if {self.from_vertex, self.to_vertex}.issubset(visited_vertex):
                    if visited_vertex.index(self.from_vertex)+1 == visited_vertex.index(self.to_vertex):
                        self.infeasible_path_list.append(path)
        else:
            for path in paths:
                if path in self.infeasible_path_list:
                    continue
                visited_vertex = list(path.visited_vertex.keys())
                # 两点都在，但是非前后关系
                if {self.from_vertex, self.to_vertex}.issubset(visited_vertex):
                    if visited_vertex.index(self.from_vertex)+1 < visited_vertex.index(self.to_vertex):
                        self.infeasible_path_list.append(path)
                # 一点在
                if self.from_vertex in visited_vertex:
                    if self.to_vertex not in visited_vertex:
                        self.infeasible_path_list.append(path)
                if self.from_vertex not in visited_vertex:
                    if self.to_vertex in visited_vertex:
                        self.infeasible_path_list.append(path)
        mp.update_feasible_paths(self.infeasible_path_list)

    def get_history_branch(self) -> list[BranchArc]:
        """
        :return: 分支的父支，包含所有arc值为0或者1的弧
        """
        branch_arcs: list[BranchArc] = []
        if self.parent is None:
            return branch_arcs
        node = self
        branch_arcs.append(node.branch_from_parent)
        while (node == node.branch_from_parent) is not None:
            if node.branch_from_parent is not None:
                branch_arcs.append(node.branch_from_parent)
        return branch_arcs

    def revise_time_matrix(self, history_branch_arcs):
        """
        :param history_branch_arcs:
        :return: new_cost_matrix
        通过传入历史访问的arcs，构建新的时间矩阵（将不可访问的弧设计为无穷，并不严格限制选取）
        """
        if self.parent is None:
            return self.ins.get_new_cost()
        # 初始化
        num_vertex = self.ins.get_num_vertex()
        new_time_matrix = copy.deepcopy(self.ins.get_new_cost())
        for arc in history_branch_arcs:
            start = arc.get_start()
            end = arc.get_end()
            if arc.value == 0:
                new_time_matrix[start][end] = Parameter.UP_max
                continue
            # 对于arc_value=1，让所有其他涉及弧端点的另外弧为无穷
            for i in range(num_vertex):
                # start,sink节点允许多次访问
                if i != start & end != num_vertex-1:
                    new_time_matrix[i][end] = Parameter.UP_max
                if start != 0 & end != i:
                    new_time_matrix[start][i] = Parameter.UP_max
        return new_time_matrix
