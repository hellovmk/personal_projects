
# In[1]:

Paths = []
Vertices = []
N = 10
d_ij = {}
full_wagons = {}
noload_rate = {}


# In[2]:
import pandas as pd
scheme = pd.read_excel("scheme.xlsx", sheetname = 1)

for i in range(len(scheme["Вершина отправления"])):
    if scheme["Вершина отправления"][i] != scheme["Вершина назначения"][i]:
        Paths.append((scheme["Вершина отправления"][i], scheme["Вершина назначения"][i]))
        d_ij[(scheme["Вершина отправления"][i], scheme["Вершина назначения"][i])] = scheme["Число груженых вагонов"][i]
        noload_rate[(scheme["Вершина отправления"][i], scheme["Вершина назначения"][i])] = int(scheme["Тариф-на-вагон, тыс.руб./вагон (за порожний пробег)"][i]*100)/100

    else:
        Vertices.append(scheme["Вершина отправления"][i])
        full_wagons[scheme["Вершина отправления"][i]] = scheme["Число груженых вагонов"][i]

# In[3]:

class Player:
    def __init__(self):
        self.y = dict.fromkeys(Paths,0)
        self.x = dict.fromkeys(Paths,0)
        self.n_kT = dict.fromkeys(Vertices,0)
    def get_freight(self):
        return self.y
    def get_noload(self):
        return self.x
    def get_amounts(self):
        return self.n_kT
    def set_path_y(self, path, val):
        self.y[path] = val
    def set_path_x(self, path, val):
        self.x[path] = val
    def set_v_n_kT(self, v, val):
        self.n_kT[v] = val
    def set_fast_y(self, values):
        for key, value in zip(list(self.y.keys()), values):
            self.y[key] = value
    def set_fast_x(self, values):
        for key, value in zip(list(self.x.keys()), values):
            self.x[key] = value
    def set_fast_n_kT(self, values):
        for key, value in zip(list(self.n_kT.keys()), values):
            self.n_kT[key] = value
    def set_all(self, values):
        self.set_fast_y(values[0:len(Paths)])
        self.set_fast_x(values[len(Paths):2*len(Paths)])
        self.set_fast_n_kT(values[2*len(Paths):len(values)])

def make_vector_from_Player(Player):
    return list(Player.get_freight().values())+list(Player.get_noload().values())+list(Player.get_amounts().values())

def make_vector(Players):
    output = list()
    for Player in Players:
        output += make_vector_from_Player(Player)
    return output

def multi_init(dic, N):
    for i in range(N):
        dic[i] = Player()

def transform_paths(dic):
    temp = Player()
    for key in dic.keys():
        temp.set_path_y(key, dic[key])
    return list(temp.get_freight().values())

def transform_vertices(dic):
    temp = Player()
    for key in dic.keys():
        temp.set_v_n_kT(key, dic[key])
    return list(temp.get_amounts().values())

def get_machine_paths():
    temp = Player()
    return list(temp.get_freight().keys())

def get_machine_vertices():
    temp = Player()
    return list(temp.get_amounts().keys())

def transliterate(name):
   """
   Автор: LarsKort
   Дата: 16/07/2011; 1:05 GMT-4;
   Не претендую на "хорошесть" словарика. В моем случае и такой пойдет,
   вы всегда сможете добавить свои символы и даже слова. Только
   это нужно делать в обоих списках, иначе будет ошибка.
   """
   # Слоаврь с заменами
   slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
      'ц':'c','ч':'cz','ш':'sh','щ':'scz','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
      'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
      'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
      'Ц':'C','Ч':'CZ','Ш':'SH','Щ':'SCZ','Ъ':'','Ы':'Y','Ь':'\'','Э':'E',
      'Ю':'YU','Я':'JA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'',
      '$':'','%':'','^':'','&':'','*':'','(':'(',')':')','-':'','=':'','+':'',
      ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
      '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
      'Є':'e'}
        
   # Циклически заменяем все буквы в строке
   for key in slovar:
      name = name.replace(key, slovar[key])
   return name

# In[4]:

d_ij_rhs = transform_paths(d_ij)


# In[5]:

Machine_paths = get_machine_paths()
Machine_vertices = get_machine_vertices()

# In[6]:

NOLOAD_CONST = transform_paths(noload_rate)

Player_costs = dict()
for i in range(N):
    Player_costs[i] = Player()
    Player_costs[i].set_fast_x(NOLOAD_CONST)

PLAYER_DUMP_0 = noload_rate.copy()
PLAYER_DUMP_0.update((x, round(y*3)) for x, y in PLAYER_DUMP_0.items())
PLAYER_DUMP_1 = noload_rate.copy()
PLAYER_DUMP_1.update((x, round(y*4)) for x, y in PLAYER_DUMP_1.items())
PLAYER_DUMP_2 = noload_rate.copy()
PLAYER_DUMP_2.update((x, round(y*5)) for x, y in PLAYER_DUMP_2.items())
PLAYER_DUMP_3 = noload_rate.copy()
PLAYER_DUMP_3.update((x, round(y*6)) for x, y in PLAYER_DUMP_3.items())
PLAYER_DUMP_4 = noload_rate.copy()
PLAYER_DUMP_4.update((x, round(y*7)) for x, y in PLAYER_DUMP_4.items())
PLAYER_DUMP_5 = noload_rate.copy()
PLAYER_DUMP_5.update((x, round(y*8)) for x, y in PLAYER_DUMP_5.items())
PLAYER_DUMP_6 = noload_rate.copy()
PLAYER_DUMP_6.update((x, round(y*9)) for x, y in PLAYER_DUMP_6.items())
PLAYER_DUMP_7 = noload_rate.copy()
PLAYER_DUMP_7.update((x, round(y*10)) for x, y in PLAYER_DUMP_7.items())
PLAYER_DUMP_8 = noload_rate.copy()
PLAYER_DUMP_8.update((x, round(y*11)) for x, y in PLAYER_DUMP_8.items())
PLAYER_DUMP_9 = noload_rate.copy()
PLAYER_DUMP_9.update((x, round(y*12)) for x, y in PLAYER_DUMP_9.items())

Player_costs[0].set_fast_y(transform_paths(PLAYER_DUMP_0))
Player_costs[1].set_fast_y(transform_paths(PLAYER_DUMP_1))
Player_costs[2].set_fast_y(transform_paths(PLAYER_DUMP_2))
Player_costs[3].set_fast_y(transform_paths(PLAYER_DUMP_3))
Player_costs[4].set_fast_y(transform_paths(PLAYER_DUMP_4))
Player_costs[5].set_fast_y(transform_paths(PLAYER_DUMP_5))
Player_costs[6].set_fast_y(transform_paths(PLAYER_DUMP_6))
Player_costs[7].set_fast_y(transform_paths(PLAYER_DUMP_7))
Player_costs[8].set_fast_y(transform_paths(PLAYER_DUMP_8))
Player_costs[9].set_fast_y(transform_paths(PLAYER_DUMP_9))
cost_vector = make_vector(list(Player_costs.values()))


# In[7]:#TYPEbound1

bounds_vector_d_ij = []
bounds_balance = []

Player_type1_bound = dict()

for path in Machine_paths:
    for i in range(N):
        Player_type1_bound[i] = Player()
        Player_type1_bound[i].set_path_y(path, 1)
    bounds_vector_d_ij.append(make_vector(list(Player_type1_bound.values())))


# In[8]:#TYPEbound2

V_in = dict()
V_out = dict()

for path in Paths:
    if path[1] not in V_in:
        V_in[path[1]] = []
    V_in[path[1]].append(path)
    if path[0] not in V_out:
        V_out[path[0]] = []
    V_out[path[0]].append(path)

Player_type2_bound = dict()

for i in range(N):
    for V in Machine_vertices:
        multi_init(Player_type2_bound, N)
        for path in V_out[V]:
            Player_type2_bound[i].set_path_y(path, 1)
            Player_type2_bound[i].set_path_x(path, 1)
        for path in V_in[V]:
            Player_type2_bound[i].set_path_y(path, -1)
            Player_type2_bound[i].set_path_x(path, -1)
        Player_type2_bound[i].set_v_n_kT(V, 1)
        bounds_balance.append(make_vector(list(Player_type2_bound.values())))


# In[9]:

PLAYER_RHS_0 = full_wagons.copy()
PLAYER_RHS_1 = full_wagons.copy()
PLAYER_RHS_2 = full_wagons.copy()
PLAYER_RHS_3 = full_wagons.copy()
PLAYER_RHS_4 = full_wagons.copy()
PLAYER_RHS_5 = full_wagons.copy()
PLAYER_RHS_6 = full_wagons.copy()
PLAYER_RHS_7 = full_wagons.copy()
PLAYER_RHS_8 = full_wagons.copy()
PLAYER_RHS_9 = full_wagons.copy()

PLAYER_RHS_0.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_0.items())
PLAYER_RHS_1.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_1.items())
PLAYER_RHS_2.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_2.items())
PLAYER_RHS_3.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_3.items())
PLAYER_RHS_4.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_4.items())
PLAYER_RHS_5.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_5.items())
PLAYER_RHS_6.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_6.items())
PLAYER_RHS_7.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_7.items())
PLAYER_RHS_8.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_8.items())
PLAYER_RHS_9.update((x, int(round(y*5/100))) for x, y in PLAYER_RHS_9.items())

right_balance_hand = {0:PLAYER_RHS_0, 
                      1:PLAYER_RHS_1,
                      2:PLAYER_RHS_2,
                      3:PLAYER_RHS_3,
                      4:PLAYER_RHS_4,
                      5:PLAYER_RHS_5,
                      6:PLAYER_RHS_6,
                      7:PLAYER_RHS_7,
                      8:PLAYER_RHS_8,
                      9:PLAYER_RHS_9}

balance_rhs = [item for sublist in [transform_vertices(dic) for dic in list(right_balance_hand.values())] for item in sublist]


# In[10]:
import pulp as pp

prob = pp.LpProblem("Primal", pp.LpMinimize)
sums = []
for i in range(N):
    sums.append(sum(list(right_balance_hand[i].values())))

Player_bounds = dict()

for i in range(N):
    Player_bounds[i] = Player()
    Player_bounds[i].set_fast_x([sums[i]]*len(Paths))

Upper_bounds = make_vector(list(Player_bounds.values()))

limit = []
for i in range(len(Upper_bounds)):
    if Upper_bounds[i] == 0:
        limit.append(None)
    else:
        limit.append(int(round(0.5*Upper_bounds[i]))) 
x = []
index = 0
for i in range(N):
    for j in range(len(Paths)):
        x.append(pp.LpVariable("freight_" + str(i+1) + "_" + transliterate(Machine_paths[j][0]) + "_" + transliterate(Machine_paths[j][1]), 0, limit[index + j], cat = pp.LpInteger))
    index += len(Paths)
    for k in range(len(Paths)):
        x.append(pp.LpVariable("noload_" + str(i+1) + "_" + transliterate(Machine_paths[k][0]) + "_" +transliterate(Machine_paths[k][1]), 0, limit[index + k], cat = pp.LpInteger))
    index += len(Paths)
    for l in range(len(Vertices)):
        x.append(pp.LpVariable("wagons_" + str(i+1) + "_in_" + transliterate(Machine_vertices[l]), 0, limit[index + l], cat = pp.LpInteger))
    index += len(Vertices)

prob += pp.lpSum([cost_vector[i]*x[i] for i in range(len(cost_vector))]), "c"
matrix = bounds_vector_d_ij + bounds_balance
b_rhs = d_ij_rhs + balance_rhs
print("initializing")
for j in range(len(d_ij_rhs + balance_rhs)):
    if j < len(d_ij_rhs):
        prob.addConstraint(pp.LpConstraint(pp.LpAffineExpression([(x[i], matrix[j][i]) for i in range(len(cost_vector)) if matrix[j][i] != 0]), rhs = b_rhs[j], name = (transliterate(Machine_paths[j][0]), transliterate(Machine_paths[j][1]))))
    else:
        prob.addConstraint(pp.LpConstraint(pp.LpAffineExpression([(x[i], matrix[j][i]) for i in range(len(cost_vector)) if matrix[j][i] != 0]), rhs = b_rhs[j], name = "VerticeN"+str(j+1-len(d_ij_rhs))))

print("proceed")
prob.writeLP("wagons.lp")
print("Status:", pp.LpStatus[prob.status])
