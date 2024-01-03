# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:39
# @Author : Pan Wuhao
from __future__ import annotations
from source.model.spdpExtension import SpdpExtension
from source.bap.bapMasterProblem import BapMasterProblem
from source.bap.PriceProblem import PriceProblem
from source.model.arc import Arc

class BapNode:
    def __init__(self, parent: BapNode, from_vertex=int, to_vertex=int, branch_value=int, ins=SpdpExtension):
        self.ins = ins
        if BapNode is not None:
            self.parent: BapNode = parent
            self.infeasible_path_list = parent.infeasible_path_list
            self.to_vertex = to_vertex
            self.from_vertex = from_vertex
            self.arc = Arc(from_vertex, to_vertex)
        else:
            self.infeasible_path_list = []
        self.isLP_feasible = True
        self.branch_from_parent = None
        self.node_num = 0

    def column_generation(self, mp=BapMasterProblem, sp=PriceProblem):
        self.update_infeasible_ptah_set(mp)

    def update_infeasible_ptah_set(self, mp):
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
