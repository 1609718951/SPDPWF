# ~/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
# @Time : 2023/12/28 14:17
# @Author : Pan Wuhao

class Path:
    def __init__(self, path: list, cost, id):
        self.visited_vertex = {}
        self.visited_arc = {}
        self.path = path
        self.cost = cost
        self.id = id
        self.init()

    def is_visited_vertex(self, i):
        if i in self.visited_vertex:
            return 1
        else:
            return 0

    def is_visited_arc(self, key):
        print(key)
        print("访问的弧", self.visited_arc[key])
        print(self.visited_arc)
        print(list(self.visited_vertex.keys()))
        if key in list(self.visited_vertex.keys()):
            return 1
        else:
            return 0

    def init(self):
        for i in self.path:
            self.visited_vertex[i] = 1
        for i in range(len(self.path) - 1):
            name = (self.path[i], self.path[i+1])
            self.visited_arc[name] = 1

    def __str__(self):
        return "path:{} \t cost:{}".format(self.path, self.cost)


if __name__ == "__main__":
    path = [0, 1, 3, 4]
    print("a")
    p = Path(path, 100, 0)
    print(p.visited_arc)
    print(p.is_visited_arc((1, 3)))