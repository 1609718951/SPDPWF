# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/13 11:30
# @Author : Pan Wuhao
from source.model.spdpInstance import Spdp


class SpdpExtension:
    def __init__(self, spdp: Spdp):
        self.instance = spdp
