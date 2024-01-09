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
from source.bap.Solution import Solution
from source.heuristic.LargeNeighborhoodSearch import LNS
from source.heuristic.ParallelConstruction import PC
from source.heuristic.GreedyGeneration import GG
from source.model.path import Path
from source.bap.bapNode import BapNode

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
        self.lower_bound = Parameter.EPS
        self.explored_node_num = 1
        "cost, bap_node"
        self.node_queue = PriorityQueue()
        self.best_node: BapNode = None
        "cost(time), path"
        self.solution_pool = PriorityQueue()

    def solve(self) -> bool:
        start_time = time.localtime()
        if not self.silent:
            print(f"branch and price:{self.version} start at {start_time}")
        initial_paths: list[Path] = []
        # 先生成对应的初始解，机遇好的初始解进行LNS操作
        paths_GG = GG(self.ins)
        paths_PC = PC(self.ins)
        if paths_PC.is_solve is False and paths_GG.is_solve is False:
            print("heuristic is failed to find a initial solution")
            return False
        if paths_GG.is_solve is not False:
            initial_paths.extend(paths_GG.get_solution())
            solution = Solution(paths_GG.time, paths_GG.get_solution())
            self.solution_pool.put([paths_GG.time, solution])
        if paths_PC.is_solve is not False:
            initial_paths.extend(paths_PC.get_solution())
            solution = Solution(paths_PC.time, paths_PC.get_solution())
            self.solution_pool.put([paths_PC.time, solution])
        # 选择进行大邻域
        if paths_GG.time < paths_PC.time:
            lns = LNS(self.ins, paths_GG.get_solution(), paths_GG.time)
        else:
            lns = LNS(self.ins, paths_PC.get_solution(), paths_PC.time)
        self.upper_bound = lns.UB
        initial_paths.extend(lns.get_solution())
        # 初始列进入主问题
        for path in initial_paths:
            self.master_problem.add_column(path)
        root = BapNode(None, 0, 0, 0, self.extension)
        if not self.silent:
            print("Root column generation starts...")
        root.column_generation(self.master_problem, self.price_problem)

        if not root.isLP_feasible:
            print("the instance is infeasible")
            return False

        # 整数解，直接加入，更新上界
        if root.is_inter_solution:
            self.best_node = root
            self.upper_bound = root.node_LPobj
            self.lower_bound = root.node_LPobj
            if not self.silent:
                print("integral solution is found by CG")
            self.solution_pool.put(self.get_node_solution(root))
        # 非整数解，更新下界,分支
        else:
            self.lower_bound = root.node_LPobj
            self.branch(root)
        # 分支之后
        while self.node_queue.empty():
            if (self.upper_bound - self.lower_bound) / self.upper_bound < Parameter.MIP_SEARCH_GAP:
                break
            node = self.node_queue.get()
            node_num = node.node_num
            self.explored_node_num = max(node_num, self.explored_node_num)
            if node.node_LPobj > self.lower_bound:
                self.lower_bound = node.node_LPobj
            self.branch(node)
        if not self.silent:
            print("finished branch and price")
        end_time = time.localtime()
        gap = (self.upper_bound - self.lower_bound)/self.upper_bound*100
        solution = self.solution_pool.get()
        self.master_problem.end()
        return True

    @staticmethod
    def get_node_solution(node: BapNode):
        """以cost, paths 获取当前节点下的路径和cost"""
        cost = node.node_LPobj
        paths = node.solution
        return cost, paths

    def branch(self, node: BapNode):
        arc_to_branch = node.arc_to_branch
        start = arc_to_branch.get_start()
        end = arc_to_branch. get_end()
        left_node = BapNode(node, start, end, 0)
        self.add_node_to_priority_queue(left_node)
        right_node = BapNode(node, start, end, 1)
        self.add_node_to_priority_queue(right_node)

    def add_node_to_priority_queue(self, new_node):
        new_node.column_generation(self.master_problem, self.price_problem)
        if not new_node.isLP_feasible:
            return
        if new_node.node_LPobj > self.upper_bound:
            return
        if new_node.is_inter_solution:
            node_num = new_node.node_num
            self.explored_node_num = max(node_num, self.explored_node_num)
            self.update_upper_bound(new_node)
            solution = Solution(self.get_node_solution(new_node))
            self.solution_pool.put((new_node.node_LPobj, solution))
            return
        self.node_queue.put(new_node.node_LPobj, new_node)

    def update_upper_bound(self, new_node):
        if new_node.node_LPobj < self.upper_bound:
            self.upper_bound = new_node.node_LPobj
            self.best_node = new_node
            self.node_log(new_node, 1)
        else:
            self.node_log(new_node, 2)

    def node_log(self, new_node, param):
        pass



