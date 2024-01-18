分支策略：
将当前所有路的各个弧访问值累计。

点集合构成：\
0: 虚拟起点\
1, vehicle_num:汽车点
vehicle_num+1, vehicle_num+order_num:取货
vehicle_num+1+order_num, vehicle_num+2*order_num:送货
vehicle_num+1+2*order_num, vehicle_num+3*order_num:取货s
vehicle_num+1+3*order_num, vehicle_num+4*order_num:送货s

