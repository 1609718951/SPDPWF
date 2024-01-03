# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:45
# @Author : Pan Wuhao
class Arc:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f"arc:{self.start}->{self.end}"
