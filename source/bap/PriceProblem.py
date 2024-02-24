# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:29
# @Author : Pan Wuhao
from source.bap.LabelSetting import LabelSetting
from source.model.spdpExtension import SpdpExtension
from source.model.path import Path


class PriceProblem:
    def __init__(self, ins: SpdpExtension):
        self.ins = ins
        self.ls = LabelSetting(ins)
        self.shortest_path: Path = None
        self.reduce_cost = 0

    def update_time_matrix(self, revise_new_time_matrix):
        self.ls.update_time_matrix(revise_new_time_matrix)

    def get_reduce_cost(self):
        return self.reduce_cost

    def get_shortest_path(self):
        return self.shortest_path

    def solve(self, dual):
        # TODO:子问题求解开始
        pass

