# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/9 10:32
# @Author : Pan Wuhao
from source.model.spdpInstance import Spdp
from source.model.parameter import Parameter


class LNS:
    def __init__(self, ins: Spdp, paths, time):
        self.is_solve = False
        self.ins = ins
        # 最优解道路[path,path]
        self.solution = []
        # 最优解的完成时间
        self.time = 0
        self.paths = paths
        self.origin_time = time
        self.UB = Parameter.UP_max

    def get_solution(self):
        return self.solution