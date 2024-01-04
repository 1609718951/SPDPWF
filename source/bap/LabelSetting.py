# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:31
# @Author : Pan Wuhao
from source.model.spdpExtension import SpdpExtension


class LabelSetting:
    def __init__(self, ins: SpdpExtension):
        self.ins = ins
        self.time_matrix = ins.get_new_cost()

    def update_time_Matrix(self, new_time_matrix):
        self.time_matrix = new_time_matrix
