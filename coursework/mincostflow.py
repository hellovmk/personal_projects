#Алгоритм Клейна(Cycle Cancelling)

import networkx as nx
from networkx.algorithms.flow import edmonds_karp
import pandas as pd
from useful import bellman_ford
import math

book = pd.read_excel("book.xlsx", sheetname = 2, index_col = "Названия строк")
demand = pd.read_excel("book.xlsx", sheetname = 0, index_col = "Узел")

target_flow = sum(demand["Из узла"][i]-demand["В узел"][i] for i in range(len(demand["Из узла"])) if demand["Из узла"][i] > demand["В узел"][i])

import_graph = nx.DiGraph()

for lead_station in book.index:
    
    for station in book[lead_station].index:
        
        if not math.isnan(book[lead_station][station]) and station != lead_station:
            import_graph.add_edge(lead_station, station, weight = book[lead_station][station], capacity = target_flow)
         
for each_station in book.index:
    
    if demand["Из узла"][each_station] < demand["В узел"][each_station]:
        import_graph.add_edge("Исток", each_station, weight = 0, capacity = abs(demand["Из узла"][each_station] - demand["В узел"][each_station]))    
    else:
        import_graph.add_edge(each_station, "Сток", weight = 0, capacity = demand["Из узла"][each_station] - demand["В узел"][each_station])

target_graph = edmonds_karp(import_graph, 'Исток', 'Сток')

check_completed = False
counter = 0
nodes = book.index
counter_for_nodes = 0
fullfil = book.index.tolist()

while not check_completed:

    counter += 1 

    residual_graph = target_graph.copy()

    for edge in residual_graph.copy().edges_iter():

        flow_dict = residual_graph.get_edge_data(*edge)["flow"]
        
        if flow_dict == residual_graph.get_edge_data(*edge)["capacity"]:
            residual_graph.remove_edge(edge[0], edge[1])
        elif flow_dict >= 0:
            residual_graph[edge[0]][edge[1]]["weight"] = import_graph[edge[0]][edge[1]]["weight"]
        if flow_dict < 0:
            residual_graph[edge[0]][edge[1]]["weight"] = -import_graph[edge[1]][edge[0]]["weight"]
    
    cycles, temp, meta = bellman_ford(residual_graph, nodes[counter_for_nodes])

    if meta == True:
        fullfil.remove(nodes[counter_for_nodes])
        
        if not fullfil:
            break
        
        if counter_for_nodes == len(nodes) - 1:
            counter_for_nodes = -1
        counter_for_nodes += 1
   
    if meta == False:
        
        box = []
        cycle_paths = []
        temp_box = []
        
        temp_graph = nx.DiGraph()
        temp_graph.add_edges_from(cycles.items())
        
        any_cycle = nx.simple_cycles(temp_graph)
        
        for cycle in any_cycle:
            
            cycle.append(cycle[0])
            
            if len(cycle) > 3:
                box = cycle
                break
        
        if not box:
            fullfil.remove(nodes[counter_for_nodes])
            
            if not fullfil:
                fullfil = book.index.tolist()
            
            if counter_for_nodes == len(nodes) - 1:
                counter_for_nodes = -1
            counter_for_nodes += 1
            
            continue
        
        
        for iter in range(len(box) - 1):
            cycle_paths.append((box[iter], box[iter + 1]))

        for edge in cycle_paths:
            
            if residual_graph.get_edge_data(edge[1], edge[0])["flow"] < 0:
                temp_box.append(0)
            else:
                temp_box.append(residual_graph.get_edge_data(edge[1], edge[0])["capacity"])
        
        flow_addition = min(temp_box[i] - residual_graph.get_edge_data(cycle_paths[i][1], cycle_paths[i][0])["flow"] for i in range(len(cycle_paths)))  
        
        for edge in cycle_paths:
            
            target_graph[edge[1]][edge[0]]["flow"] += flow_addition
            target_graph[edge[0]][edge[1]]["flow"] -= flow_addition     

summa = 0
output = open('solution_by_me.txt', 'w')

for edge in target_graph.edges():
    
    inner_flow = target_graph.get_edge_data(*edge)["flow"]
    
    if inner_flow > 0 and 'Исток' not in edge and 'Сток' not in edge:
        print(edge[0], " ->", edge[1], ": ",  inner_flow, file = output)
        summa += inner_flow*import_graph.get_edge_data(*edge)["weight"]

output.close()
print(counter, " iterations taken")
print(summa)
