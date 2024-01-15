# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/9 10:32
# @Author : Pan Wuhao
from source.model.spdpExtension import SpdpExtension, Spdp


class PC:
    def __init__(self, ins: SpdpExtension):
        self.is_solve = False
        self.ins = ins
        self.solution = None
        self.time = 0

    def get_solution(self):
        return self.solution
