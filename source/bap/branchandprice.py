# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/1/3 10:32
# @Author : Pan Wuhao
from source.model.spdpInstance import Spdp
from source.model.spdpExtension import SpdpExtension
from source.bap.bapMasterProblem import BapMasterProblem
from source.bap.PriceProblem import PriceProblem
from source.model.parameter import Parameter
from queue import PriorityQueue
from source.heuristic.LargeNeighborhoodSearch import LNS
from source.heuristic.ParallelConstruction import PC
import time


class BranchAndPrice:
    version = "24.1.8"
    # 是否输出版本信息
    silent = True

    def __init__(self, ins: Spdp):
        self.ins = ins
        self.extension = SpdpExtension(ins)
        self.master_problem = BapMasterProblem(self.extension)
        self.price_problem = PriceProblem(self.extension)
        self.upper_bound = Parameter.UP_max
        self.explored_node_num = 1
        self.node_queue = []
        "cost(time), path"
        self.solution_pool = PriorityQueue()

    def solve(self) -> bool:
        start_time = time.localtime()
        if not self.silent:
            print(f"branch and price:{self.version} start at {start_time}")
        initial_paths = []
        paths_LNS = LNS(self.ins)
        paths_PC = PC(self.ins)
        if paths_PC.is_solve is False and paths_LNS.is_solve is False:
            print("heuristic is failed to find a initial solution")
            return False
        if paths_LNS.is_solve is not False:
            initial_paths.extend(paths_LNS.get_solution())
            self.solution_pool.put(paths_LNS.time, paths_LNS.get_solution())
        if paths_PC.is_solve is not False:
            initial_paths.extend(paths_PC.get_solution())
            self.solution_pool.put(paths_LNS.time, paths_LNS.get_solution())


