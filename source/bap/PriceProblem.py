# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:29
# @Author : Pan Wuhao
from source.bap.LabelSetting import LabelSetting
from source.model.spdpExtension import SpdpExtension


class PriceProblem:
    def __init__(self, ins: SpdpExtension):
        self.ins = ins
        self.ls = LabelSetting(ins)

    def update_time_matrix(self, revise_new_time_matrix):
        self.ls.update_time_Matrix(revise_new_time_matrix)

