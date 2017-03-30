#Алгоритм Клейна(Cycle Cancelling)

#библиотеки
import networkx as nx
from networkx.algorithms.flow import edmonds_karp
import pandas as pd
from useful import bellman_ford
import math

#чтение excel
book = pd.read_excel("book.xlsx", sheetname = 1, index_col = "Названия строк")
demand = pd.read_excel("book.xlsx", sheetname = 0, index_col = "Узел")

#пропускная способность для каждой железной дороги
target_flow = sum(demand["Из узла"][i]-demand["В узел"][i] for i in range(len(demand["Из узла"])) if demand["Из узла"][i] > demand["В узел"][i])

#создание неориентированного графа
import_graph = nx.Graph()

#создание дуг и вершин
for lead_station in book.index:
    for station in book[lead_station].index:
        if not math.isnan(book[lead_station][station]) and station != lead_station:
            import_graph.add_edge(lead_station, station, weight = book[lead_station][station], capacity = target_flow)
            
#соединение стока и истока для "-" и "+"
for each_station in book.index:
    if demand["Из узла"][each_station] < demand["В узел"][each_station]:
        import_graph.add_edge("Исток", each_station, weight = 0, capacity = abs(demand["Из узла"][each_station] - demand["В узел"][each_station]))    
    else:
        import_graph.add_edge(each_station, "Сток", weight = 0, capacity = demand["Из узла"][each_station] - demand["В узел"][each_station])
        
#нахождение макс потока методом Едмондса-Карпа; поток получится произвольный с заданной величиной
target_graph = edmonds_karp(import_graph, 'Исток', 'Сток')

#заготовки
check_completed = False
counter = 0
nodes = book.index
counter_for_nodes = 0

#главный цикл
while not check_completed:
    
    #каждый раз строится остаточная сеть
    residual_graph = target_graph.copy()
    
    #количество итераций
    counter += 1
    
    #тут взвешиваются и распознаётся какая дуга прямая, а какая обратная
    for edge in residual_graph.edges_iter():
        flow_dict = residual_graph.get_edge_data(*edge)["flow"]
        if flow_dict <= 0:
            residual_graph[edge[1]][edge[0]]["weight"] = import_graph[edge[1]][edge[0]]["weight"]
            if flow_dict != 0:
                residual_graph[edge[0]][edge[1]]["weight"] = -import_graph[edge[1]][edge[0]]["weight"]    
                residual_graph[edge[0]][edge[1]]["capacity"] = 0
    
    #тут удаляется из сети дуга с нулевой остаточной пропускной способностью
    for edge in residual_graph.copy().edges_iter():
        flow_dict = residual_graph.get_edge_data(*edge)["flow"]
        capacity_dict = residual_graph.get_edge_data(*edge)["capacity"]
        if capacity_dict == flow_dict:
            residual_graph.remove_edge(edge[0], edge[1])
            
    #к получившейся сети применяется алгоритм Беллмана-Форда, чтобы найти циклы с отрицательной 
    #стоимостью; алгоритм скорее будет достаточным условием, потому что циклами он еще считает бесплатные
    #дуги, например, которые идут из стока, и вдобавок те, которые в сумме дают ноль
    cycles, temp, meta = bellman_ford(residual_graph, nodes[counter_for_nodes])
    check_completed = meta
    
    #если Беллман-Форд сказал, что отрицательных циклов больше нет, то ура - решение найдено
    if check_completed == False:
        
        #заготовки        
        box = []
        cycle_paths = []
        
        #представляем отрицательные циклы как ориентированный граф
        temp_graph = nx.DiGraph()
        temp_graph.add_edges_from(cycles.items())
        
        #в этом графе находим простой цикл
        any_cycle = nx.simple_cycles(temp_graph)
        
        #так как simple_cycles ищет все циклы - находим первый попавшийся нужный
        for cycle in any_cycle:
            cycle.append(cycle[0])
            if len(cycle) > 3:
                box = cycle
                break
        
        #если нужных нет - значит вершина уже себя исчерпала(недостаток Беллмана-Форда)
        #приходится брать другую
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
        
        #цикл представим в виде последовательности дуг
        for iter in range(len(box) - 1):
            cycle_paths.append((box[iter], box[iter + 1]))
        
        #находим минимум по всем остаточным пропускным способностям - его надо "вгрузить" в цикл
        flow_addition = min([abs(residual_graph.get_edge_data(cycle_paths[i][1], cycle_paths[i][0])["capacity"] - residual_graph.get_edge_data(cycle_paths[i][1], cycle_paths[i][0])["flow"])] for i in range(len(cycle_paths)))  
        
        #добавляем в отрицательный цикл поток
        for edge in cycle_paths:
            target_graph[edge[1]][edge[0]]["flow"] += flow_addition[0]
            target_graph[edge[0]][edge[1]]["flow"] = -target_graph[edge[1]][edge[0]]["flow"]     

#вывод ответа 
for edge in target_graph.edges():
    inner_flow = target_graph.get_edge_data(*edge)["flow"]
    if inner_flow > 0 and 'Исток' not in edge and 'Сток' not in edge:
        print(edge[0], " ->", edge[1], ": ",  inner_flow)

#количество итераций
print(counter, " iterations taken")

#сложность : что-то около O(e^2*n*C*U), где e - количество дуг, n - вершин, C - максимальная пропускная, U - максимальная стоимость