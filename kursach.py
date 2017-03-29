import networkx as nx
from networkx.algorithms.flow import edmonds_karp
import pandas as pd
from useful import bellman_ford
import math

book = pd.read_excel("book.xlsx", sheetname = 1, index_col = "Названия строк")
demand = pd.read_excel("book.xlsx", sheetname = 0, index_col = "Узел")

import_graph = nx.Graph()
target_flow = sum(demand["Из узла"][i]-demand["В узел"][i] for i in range(len(demand["Из узла"])) if demand["Из узла"][i] > demand["В узел"][i])

for lead_station in book.index:
    for station in book[lead_station].index:
        if not math.isnan(book[lead_station][station]) and station != lead_station:
            import_graph.add_edge(lead_station, station, weight = book[lead_station][station], capacity = target_flow)
            

for each_station in book.index:
    if demand["Из узла"][each_station] < demand["В узел"][each_station]:
        import_graph.add_edge("Исток", each_station, weight = 0, capacity = abs(demand["Из узла"][each_station] - demand["В узел"][each_station]))    
    else:
        import_graph.add_edge(each_station, "Сток", weight = 0, capacity = demand["Из узла"][each_station] - demand["В узел"][each_station])
        


'''import_graph.add_edge('X','A', capacity=11, weight=0)
import_graph.add_edge('X','B', capacity=7, weight=0)
import_graph.add_edge('X','C', capacity=2, weight=0)
import_graph.add_edge('X','D', capacity=8, weight=0)
import_graph.add_edge('A','B', capacity=28, weight=1)
import_graph.add_edge('B','C', capacity=28, weight=2)
import_graph.add_edge('D','C', capacity=28, weight=4)
import_graph.add_edge('C','E', capacity=15, weight=3)
import_graph.add_edge('A','F', capacity=13, weight=1)
import_graph.add_edge('F','Y', capacity=13, weight=0)
import_graph.add_edge('E','Y', capacity=15, weight=0)
import_graph.add_edge('D','F', capacity=13, weight=50)
import_graph.add_edge('B','F', capacity=13, weight=10)'''


'''import_graph.add_edge('X','A', capacity=100, weight=0)
import_graph.add_edge('X','B', capacity=20, weight=0)
import_graph.add_edge('A','B', capacity=100, weight=1)
import_graph.add_edge('A','C', capacity=40, weight=1)
import_graph.add_edge('A','D', capacity=40, weight=3)
import_graph.add_edge('A','E', capacity=40, weight=100)
import_graph.add_edge('B','C', capacity=40, weight=3)
import_graph.add_edge('B','D', capacity=40, weight=1)
import_graph.add_edge('B','E', capacity=40, weight=1)
import_graph.add_edge('E','Y', capacity=40, weight=0)
import_graph.add_edge('D','Y', capacity=40, weight=0)
import_graph.add_edge('C','Y', capacity=40, weight=0)'''

target_graph = edmonds_karp(import_graph, 'Исток', 'Сток')

check_completed = False
counter = 0
nodes = book.index
counter_for_nodes = 0

while not check_completed:
    residual_graph = target_graph.copy()
    print(counter + 1, " Iterations")
    counter += 1
    for edge in residual_graph.edges_iter():
        flow_dict = residual_graph.get_edge_data(*edge)["flow"]
        if flow_dict <= 0:
            residual_graph[edge[1]][edge[0]]["weight"] = import_graph[edge[1]][edge[0]]["weight"]
            if flow_dict != 0:
                residual_graph[edge[0]][edge[1]]["weight"] = -import_graph[edge[1]][edge[0]]["weight"]    
                residual_graph[edge[0]][edge[1]]["capacity"] = 0
            
    for edge in residual_graph.copy().edges_iter():
        flow_dict = residual_graph.get_edge_data(*edge)["flow"]
        capacity_dict = residual_graph.get_edge_data(*edge)["capacity"]
        if capacity_dict == flow_dict:
            residual_graph.remove_edge(edge[0], edge[1])
    cycles, temp, meta = bellman_ford(residual_graph, nodes[counter_for_nodes])
    check_completed = meta
    decrease = False
    if check_completed == False:
        box = []
        cycle_paths = []
        temp_graph = nx.DiGraph()
        temp_graph.add_edges_from(cycles.items())
        cycles_2 = nx.simple_cycles(temp_graph)
        for cycle in cycles_2:
            cycle.append(cycle[0])
            if len(cycle) > 3:
                box = cycle
                break
        if not box:
            if counter_for_nodes == len(nodes):
                decrease = True
            if counter_for_nodes == 0:
                decrease = False
            if decrease:
                counter_for_nodes -= 1
            else:
                counter_for_nodes += 1
            continue            
        for iter in range(len(box) - 1):
            cycle_paths.append((box[iter], box[iter + 1]))
        flow_addition = min([abs(residual_graph.get_edge_data(cycle_paths[i][1], cycle_paths[i][0])["capacity"] - residual_graph.get_edge_data(cycle_paths[i][1], cycle_paths[i][0])["flow"])] for i in range(len(cycle_paths)))  
        for edge in cycle_paths:
            target_graph[edge[1]][edge[0]]["flow"] += flow_addition[0]
            target_graph[edge[0]][edge[1]]["flow"] = -target_graph[edge[1]][edge[0]]["flow"]

for edge in target_graph.edges():
    inner_flow = target_graph.get_edge_data(*edge)["flow"]
    if inner_flow > 0 and 'Исток' not in edge and 'Сток' not in edge:
        print(edge[0], " ->", edge[1], ": ",  inner_flow)
    ''''''