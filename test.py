
import networkx as nx
import pandas as pd
import math
import numpy as np
from scipy.optimize import linprog


book = pd.read_excel("book.xlsx", sheetname = 1, index_col = "Названия строк")
demand = pd.read_excel("book.xlsx", sheetname = 0, index_col = "Узел")

target_flow = sum(demand["Из узла"][i]-demand["В узел"][i] for i in range(len(demand["Из узла"])) if demand["Из узла"][i] > demand["В узел"][i])

import_graph = nx.DiGraph()

counter = 0
for i in book.index:
    import_graph.add_node(i, demand = demand["В узел"][i] - demand["Из узла"][i])
for lead_station in book.index:
    for station in book[lead_station].index:
        if not math.isnan(book[lead_station][station]) and station != lead_station:
            import_graph.add_edge(lead_station, station, weight = book[lead_station][station], capacity = target_flow)
            counter += 1
A = np.zeros((len(book.index), counter))

i = 0
j = 0
for each_node in book.index:
    for edges in import_graph.edges():
        if each_node == edges[0]:
            A[i][j] = 1
        elif each_node == edges[1]:
            A[i][j] = -1
        j += 1
    j = 0
    i += 1

cost = np.zeros(counter)
index = 0
for edges in import_graph.edges():
    cost[index] = import_graph.get_edge_data(*edges)["weight"]
    index += 1
index = 0
node_demand = np.zeros(len(book.index))
for node in book.index:
    node_demand[index] = import_graph.node[node]["demand"]        
    index += 1
sequence = []    
for i in import_graph.edges():
    sequence.append((0, target_flow))
solution = linprog(cost, A_eq = A, b_eq = node_demand, bounds = sequence).x
output = open('solution_by_lp.txt', 'w')
for i in range(len(solution)):
    if solution[i] > 0:
        print(import_graph.edges()[i], "->", solution[i], file = output)
        
output.close()