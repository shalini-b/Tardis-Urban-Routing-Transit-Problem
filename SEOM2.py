import random
class node:
    def __init__(self):
        self.posx = -1
        self.posy = -1
        self.id = -1
        self.neighbours = []
class route:
    def __init__(self):
        self.start = None
        self.end = None
        self.length = 0
        self.path_nodes = []
def check_conditions(rout,length):
    if(rout.length >= length):
        return False
    if rout.start.neighbours.size ==0 and rout.end.neighbours.size == 0:
        return False
    for i in rout.start.neighbours:
        if i not in rout.path_nodes:
            return True
    for j in rout.end.neighbours:
        if j not in rout.path_nodes:
            return True
    return False

def generate_initialpopulation(MIN,MAX):
    rand_size = random.randrange(MIN,MAX)
    temp = nodes[random.randrange(0,size-1)]
    new_route = route()
    new_route.start = temp
    while(check_conditions(new_route,rand_size)):
        if new_route.start.neighbours.size == 0:
            temp = new_route.start
            new_route.start = new_route.end
            new_route.end = temp
            continue
        temp2 = new_route.start.neighbours[random.randrange(0,new_route.start.neighbours-1)]
        if temp2 not in new_route.path_nodes:
            new_route.path_nodes.append(temp2)

size = 0
inp = "/Users/SrinikhilReddy/Downloads/CEC2013Supp/Instances/MandlCoords.txt"
in_p = open(inp,'r')
x = in_p.readline().split()
nodes = []
size = int(x[0])
for i in range(0,size):
    temp = node()
    temp.id = 1
    nodes.append(temp)
travel_times = [[0 for x in range(size)] for y in range(size)]
demand = [[0 for x in range(size)] for y in range(size)]
inp2 = "/Users/SrinikhilReddy/Downloads/CEC2013Supp/Instances/MandlTravelTimes.txt"
i = 0
with open(inp2,'r') as in_p2:
    for x in in_p2:
        x = x.split()
        if x:
            for j in range(0,size):
                if x[j] == 'Inf' or x[j] == '0':
                    continue
                travel_times[i][j] = int(x[j])
                nodes[i].neighbours.append(nodes[j])
            i = i+1
inp3 = "/Users/SrinikhilReddy/Downloads/CEC2013Supp/Instances/MandlDemand.txt"
i = 0
with open(inp3,'r') as in_p2:
    for x in in_p2:
        x = x.split()
        if x:
            for j in range(0,size):
                if x[j] == 'Inf':
                    continue
                demand[i][j] = int(x[j])
            i = i+1

