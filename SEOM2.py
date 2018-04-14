import random


class Node(object):
    def __init__(self, id, posx, posy):
        self.posx = posx
        self.posy = posy
        self.id = id
        self.neighbours = []


class Route(object):
    def __init__(self):
        self.start = None
        self.end = None
        self.length = 0
        self.path_nodes = []


class TransitGraph(object):
    def __init__(self, nodes, demand, travel_times):
        self.nodes = nodes
        self.demand = demand
        self.travel_times = travel_times

    @staticmethod
    def check_conditions(route, length):
        if route.length >= length:
            return False
        if route.start.neighbours.size == 0 and route.end.neighbours.size == 0:
            return False
        for j in route.end.neighbours:
            if j not in route.path_nodes:
                return True
        for i in route.start.neighbours:
            if i not in route.path_nodes:
                return True
        return False

    def generate_initial_population(self, MIN, MAX):
        rand_size = random.randrange(MIN, MAX)
        temp = nodes[random.randrange(0, size-1)]
        new_route = Route()
        new_route.start = temp
        new_route.end = new_route.start
        while self.check_conditions(new_route, rand_size):
            if new_route.start.neighbours.size == 0:
                temp = new_route.start
                new_route.start = new_route.end
                new_route.end = temp
                continue
            temp2 = new_route.end.neighbours[random.randrange(0, new_route.start.neighbours-1)]
            if temp2 not in new_route.path_nodes:
                new_route.path_nodes.append(temp2)
                new_route.end = temp2


if __name__ == '__main__':
    nodes = []
    with open('MandlCoords.txt') as f:
        size = int(f.readline().split()[0])
        id = 1
        for coords in f.readlines():
            posx, posy = list(map(int, coords.split()))
            nodes.append(Node(id, posx, posy))
            id += 1

    travel_times = [[0] * size] * size
    demand = [[0] * size] * size

    with open('MandlTravelTimes.txt') as in_p2:
        i = 0
        for row in in_p2.readlines():
            if not row.strip():
                continue
            for j, val in enumerate(row.split()):
                if val in ['Inf', '0']:
                    continue
                travel_times[i][j] = int(val)
                nodes[i].neighbours.append(nodes[j])
            i += 1

    with open('MandlDemand.txt') as in_p3:
        i = 0
        for row in in_p3.readlines():
            if not row.strip():
                continue
            for j, val in enumerate(row.split()):
                if val in ['Inf', '0']:
                    continue
                demand[i][j] = int(val)
            i += 1

    TransitGraph(nodes, demand, travel_times)