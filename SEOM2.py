import random
import copy
from functools import reduce


class Node(object):
    def __init__(self, id, posx, posy):
        self.id = id
        self.posx = posx
        self.posy = posy
        self.neighbours = []


class RouteSet(object):
    def __init__(
            self,
            num_routes,
            min_route_len,
            max_route_len,
            num_nodes,
            demand):
        self.num_routes = num_routes
        self.min_route_len = min_route_len
        self.max_route_len = max_route_len
        self.shortest_path_times = copy.deepcopy(travel_times)
        self.num_nodes = num_nodes
        # Contains IDs of chosen nodes till now
        self.chosen = set()
        # Contains route objects for this routeset
        self.routes = []
        # Maintains a map of node & routes it is present in
        self.node_map = {}
        self.demand = demand
        self.passengerCost=0
        self.operatorCost=0

    def __eq__(self, other):
        # Check if number of routes are same in both
        if len(self.routes) != len(other.routes):
            return False

        # Check if the overall nodes in both are same
        if self.chosen != other.chosen:
            return False

        # Check if the individual paths are same in both
        # by comparing their hashed IDs
        if set(map(lambda x: x.hashed_id, self.routes)) != set(map(lambda x: x.hashed_id, other.routes)):
            return False

        return True

    def computePassengerCost(self):
        numerator = 0
        denominator = 1
        for i in range(0,self.num_nodes):
            for j in range(0, self.num_nodes):
                numerator+=(demand[i][j]*self.shortest_path_times[i][j])
                denominator+=demand[i][j]

        self.passengerCost = numerator/denominator

    def OperatorCost(self):
        sum=0
        for route in self.routes:
            for i in range(0,len(route.path_nodes)-1,2):
                sum+= self.shortest_path_times[i][i+1]
        self.operatorCost = sum         

    def recalculate_chosen_nodes(self):
        self.chosen = set()
        self.chosen.update([node.id for route in self.routes for node in route.path_nodes])

    def generate_routeset(self):
        # Create a route on every iteration
        for count in range(self.num_routes):
            # Select random size for route
            route_len = random.randrange(self.min_route_len, self.max_route_len)

            if count == 0:
                # Select the starting node for the first route
                cur_node = nodes[random.randrange(size)]
                # Create node
                route = Route(cur_node)
            else:
                # Select the starting node for an adjoining route
                # from the list of chosen nodes to ensure connectivity
                cur_node = nodes[random.choice(list(self.chosen)) - 1]
                # Create node
                route = Route(cur_node)
                route.connecting_nodes.append(cur_node)

            # Update node map and chosen with new route and node
            self.node_map.setdefault(cur_node.id, []).append(route)
            self.chosen.add(cur_node.id)
            # Add to routes
            self.routes.append(route)

            route_reversed = False
            while len(route.path_nodes) < route_len:
                next_nodes = route.fetch_next_nodes(cur_node)
                if not next_nodes:
                    if not route_reversed:
                        route.reverse_route()
                        route_reversed = True
                    else:
                        # Adding at both ends tested, leave
                        break
                else:
                    next_node = random.choice(next_nodes)
                    # Update node map and chosen with new route and node
                    route.append_to_path_end(next_node)
                    if self.node_map.get(next_node):
                        route.connecting_nodes.append(next_node)
                        for r in self.node_map[next_node]:
                            r.connecting_nodes.append(next_node)

                    self.node_map.setdefault(next_node.id, []).append(route)
                    self.chosen.add(next_node.id)
                    cur_node = next_node
        if len(self.chosen) < self.num_nodes:
            self.repair()
            if len(self.chosen) < self.num_nodes:
                return False
            else:
                return True
        return True


    def add_nodes(self):
        # Choose a random number of nodes to add
        count = random.randrange(1, (self.max_route_len * self.num_routes) // 2)

        routes_checked = []
        while count > 0:
            # Check if all routes are exhausted for addition
            if len(routes_checked) == len(self.routes):
                break

            # Select the route not checked till now
            rand_route = self.routes[random.randrange(len(self.routes))]
            while rand_route in routes_checked:
                rand_route = self.routes[random.randrange(len(self.routes))]

            # Append it to routes checked
            routes_checked.append(rand_route)

            # Add nodes at the end/start of the route if possible
            route_reversed = False
            # Checking if the length of route is lesser than
            # max_route_len mentioned by user
            while len(rand_route.path_nodes) <= self.max_route_len:
                next_nodes = rand_route.fetch_next_nodes(rand_route.end)
                if not next_nodes:
                    # Reverse the route & try adding at the start
                    if not route_reversed:
                        rand_route.reverse_route()
                        route_reversed = True
                    else:
                        # Adding at both ends tested, leave
                        break
                else:
                    next_node = random.choice(next_nodes)
                    rand_route.append_to_path_end(next_node)
                    if self.node_map.get(next_node):
                        rand_route.connecting_nodes.append(next_node)
                        for r in self.node_map[next_node]:
                            r.connecting_nodes.append(next_node)

                    self.node_map.setdefault(next_node.id, []).append(rand_route)
                    self.chosen.add(next_node.id)
                    count -= 1

    def delete_nodes(self):
        # Choose a random number of nodes to add
        count = random.randrange(1, (self.max_route_len * self.num_routes) // 2)

        routes_checked = []
        while count > 0:
            # Check if all routes are exhausted for removal
            if len(routes_checked) == self.num_routes:
                break

            # Select the route not checked till now
            rand_route = self.routes[random.randrange(self.num_routes)]
            while rand_route in routes_checked:
                rand_route = self.routes[random.randrange(self.num_routes)]

                # Append it to routes checked
                routes_checked.append(rand_route)

                # Add nodes at the end/start of the route if possible
                route_reversed = False
                # Checking if the length of route is greater than
                # min_route_len mentioned by user
                while len(rand_route.path_nodes) >= self.min_route_len:
                    # TODO: change from here
                    if not self.check_for_node_deletion(rand_route):
                        # Reverse the route & try adding at the start
                        if not route_reversed:
                            rand_route.reverse_route()
                            route_reversed = True
                        else:
                            # Adding at both ends tested, leave
                            break
                    else:
                        # rand_route.append_to_path_end(next_node)
                        # self.chosen.add(next_node.id)
                        count -= 1

    def check_for_node_deletion(self, route):
        # Check if the node at route end is duplicated and can be
        # removed without breaking the connectivity of routeset
        if len(self.node_map[route.end]) <= 1:
            return False

        return True

    def swap_routes(self, routeset_to_add, target_route):
        # Add target_route from current one to routeset_to_add
        routeset_to_add.routes.append(target_route)
        routeset_to_add.chosen.update(map(lambda x: x.id, target_route.path_nodes))

        # Remove target_route from current one
        self.routes.remove(target_route)
        self.recalculate_chosen_nodes()

    def repair(self):
        routes_checked = []
        while len(self.chosen) <= self.num_nodes:
            # Check if all routes are exhausted for addition
            if len(routes_checked) == len(self.routes):
                break

            # Select the route not checked till now
            rand_route = self.routes[random.randrange(self.num_routes)]
            while rand_route in routes_checked:
                rand_route = self.routes[random.randrange(self.num_routes)]

            # Append it to routes checked
            routes_checked.append(rand_route)

            # Add nodes at the end/start of the route if possible
            route_reversed = False
            # Checking if the length of route is lesser than
            # max_route_len mentioned by user
            while len(rand_route.path_nodes) <= self.max_route_len:
                next_nodes = rand_route.fetch_next_nodes(rand_route.end)
                if not next_nodes:
                    # Reverse the route & try adding at the start
                    if not route_reversed:
                        rand_route.reverse_route()
                        route_reversed = True
                    else:
                        # Adding at both ends tested, leave
                        break
                else:
                    next_node = random.choice(next_nodes)
                    rand_route.append_to_path_end(next_node)
                    self.node_map.setdefault(next_node.id, []).append(rand_route)
                    self.chosen.add(next_node.id)


    def generate_shortest_path_pairs(self):
        for k in range(self.num_nodes):
            for i in range(self.num_nodes):
                for j in range(self.num_nodes):
                    dist = self.shortest_path_times[i][k] + self.shortest_path_times[k][j]
                    if dist >= self.shortest_path_times[i][j]:
                        continue
                    if set(self.node_map[i+1]).intersection(set(self.node_map[j+1])):
                        self.shortest_path_times[i][j] = \
                            self.shortest_path_times[i][k] + self.shortest_path_times[k][j]
                    else:
                        # if i & j are in different paths, add 5 as penalty
                        self.shortest_path_times[i][j] = \
                            self.shortest_path_times[i][k] + self.shortest_path_times[k][j] + 5


class Route(object):
    def __init__(self, node):
        self.start = node
        self.end = node
        self.connecting_nodes = []
        self.path_nodes = [node]

    @property
    def hashed_id(self):
        # Unique ID for the route to identify different variations of it
        return sum(map(lambda x: x.id, self.path_nodes))

    def fetch_next_nodes(self, cur_node):
        options = []
        for n in cur_node.neighbours:
            # TODO: Check if this works
            if n not in self.path_nodes:
                options.append(n)
        return options

    def reverse_route(self):
        self.start, self.end = self.end, self.start
        self.path_nodes.reverse()

    def append_to_path_end(self, node):
        self.path_nodes.append(node)
        self.end = node


class TransitGraph(object):
    def __init__(
            self,
            nodes,
            demand,
            travel_times):
        # NOTE: Do not change the order of nodes in this list
        self.nodes = nodes
        self.num_nodes = len(nodes)
        self.demand = demand
        self.travel_times = travel_times
        self.routesets = []

    def create_initial_population(
            self,
            num_routesets,
            num_routes,
            min_route_len,
            max_route_len):
        count = 0
        # Create an array of routesets
        while count <= num_routesets:
            rs = RouteSet(
                num_routes,
                min_route_len,
                max_route_len,
                self.num_nodes,
                demand)
            if rs.generate_routeset():
                self.routesets.append(rs)
                count+=1

    @staticmethod
    def pick_best(parent, offspring):
        best_val = 0
        target = None

        # Finding the best route in parent wrt offspring
        for route in parent.routes:
            # Find the number of common nodes between the
            # selected route of parent and the offspring routeset
            common_nodes_len = len(set(map(lambda x: x.id, route.path_nodes)).intersection(offspring.chosen))
            if common_nodes_len >= 1:
                route_len = len(route.path_nodes)
                target_len = (route_len - common_nodes_len)/route_len
                if target_len >= best_val:
                    target = route
                    best_val = target_len

        return target

    def crossover(self, parent1, parent2):
        # Create a offspring
        offspring = RouteSet(
            parent1.num_routes,
            parent1.min_route_len,
            parent1.max_route_len,
            parent1.num_nodes,
            demand)

        # Take copies of both parents so as to not manipulate them
        p1 = copy.deepcopy(parent1)
        p2 = copy.deepcopy(parent2)

        # Choose a random route from parent1 and add it to offspring
        seed_route = random.choice(p1.routes)

        # Remove seed_route from parent1 and add to offspring
        p1.swap_routes(offspring, seed_route)
        while len(offspring.routes) < offspring.num_routes:
            if len(offspring.routes) % 2 == 1:
                # Pick the best route available in P2
                # which is not present in offspring yet
                best_route = self.pick_best(p2,offspring)
                while best_route in offspring.routes:
                    best_route = self.pick_best(p2,offspring)
                if best_route:
                # Remove best_route from parent2 and add to offspring
                    p2.swap_routes(offspring, best_route)
                else:
                    exit(1)
            else:
                # Pick the best route available in P2
                # which is not present in offspring yet
                best_route = self.pick_best(p1,offspring)
                while best_route in offspring.routes:
                    best_route = self.pick_best(p1,offspring)
                if best_route:
                    # Remove best_route from parent1 and add to offspring
                    p1.swap_routes(offspring, best_route)
                else:
                    exit(1)

        return offspring


if __name__ == '__main__':
    # List of node objects
    nodes = []
    with open('MandlCoords.txt') as f:
        # Number of nodes
        size = int(f.readline().split()[0])
        for id, coords in enumerate(f.readlines()):
            posx, posy = list(map(float, coords.split()))
            # Populate list of nodes
            # NOTE: id of nodes is different from the one listed in coords file
            nodes.append(Node(id + 1, posx, posy))

    # Travel time defined from src to dest if applicable, 0 otherwise
    travel_times = [[0 for x in range(size)] for y in range(size)]
    # Signifies demand between two places
    demand = [[0 for x in range(size)] for y in range(size)]

    with open('MandlTravelTimes.txt') as in_p2:
        i = 0
        for row in in_p2.readlines():
            # Input has blank rows in between - skipping them
            if not row.strip():
                continue

            for j, val in enumerate(row.split()):
                if val == 'Inf':
                    val = 9999
                travel_times[i][j] = int(val)
                # TODO: Is it a better idea to just put the ID
                # Update neighbours of nodes - for nw putting the objects
                if val!=9999:
                    nodes[i].neighbours.append(nodes[j])
            i += 1

    with open('MandlDemand.txt') as in_p3:
        i = 0
        for row in in_p3.readlines():
            # Input has blank rows in between - skipping them
            if not row.strip():
                continue

            for j, val in enumerate(row.split()):
                if val == 'Inf':
                    val = 9999
                demand[i][j] = int(val)
            i += 1

    # Number of routeset combinations
    num_routesets = int(input('Number of routesets: '))
    # Number of routes in each routeset
    num_routes = int(input('Number of routes in each routeset: '))
    # Maximum and minimum number of routes in route set
    min_route_len, max_route_len = list(map(int, input('Input minimum and maximum route length: ').split()))

    transit_map = TransitGraph(nodes, demand, travel_times)
    transit_map.create_initial_population(num_routesets, num_routes, min_route_len, max_route_len)
    for rs in transit_map.routesets:
        rs.generate_shortest_path_pairs()
    for j in range(1,100):
        for i in transit_map.routesets:
            Parent1 = i
            Parent2 = transit_map.routesets[random.randrange(len(transit_map.routesets))]
            os = transit_map.crossover(Parent1, Parent2)
            os.repair()
            for i in os.routes:
                print([j.id for j in i.path_nodes])
            flag = False
            for k in transit_map.routesets:
                if k == os:
                    flag = True
            if flag:
                print("WOwzazazaza")
                continue
            #os.generate_shortest_path_pairs()

