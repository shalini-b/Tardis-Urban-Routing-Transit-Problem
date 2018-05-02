import random


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
            num_nodes):
        self.num_routes = num_routes
        self.min_route_len = min_route_len
        self.max_route_len = max_route_len
        self.num_nodes = num_nodes
        # Contains IDs of chosen nodes till now
        self.chosen = []
        self.routes = []
        self.generate_routeset()

    def generate_routeset(self):
        # Create a route on every iteration
        for count in range(self.num_routes):
            # Select random size for route
            route_len = random.randrange(self.min_route_len, self.max_route_len)

            if count == 0:
                # Select the starting node for the first route
                cur_node = nodes[random.randrange(size)]
            else:
                # Select the starting node for an adjoining route
                # from the list of chosen nodes to ensure connectivity
                cur_node = nodes[random.choice(self.chosen)]

            route = Route(cur_node)
            self.chosen.append(cur_node.id)
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
                    # TODO: if we need sequential path nodes even
                    # after reversing, we need reverse path_nodes list too
                    route.append_to_path_end(next_node)
                    self.chosen.append(next_node.id)
                    cur_node = next_node

        if len(self.chosen) < self.num_nodes:
            res = self.repair()
            return self.routes if res else []

    def add_nodes(self):
        # Choose a random number of nodes to add
        count = random.randrange(1, (self.max_route_len * self.num_routes) // 2)

        routes_checked = []
        while count > 0:
            # Check if all routes are exhausted for addition
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
            # Checking if the length of route is lesser than
            # max_route_len mentioned by user
            while len(rand_route.path_nodes) < self.max_route_len:
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
                    # TODO: if we need sequential path nodes even
                    # after reversing, we need reverse path_nodes list too
                    rand_route.append_to_path_end(next_node)
                    self.chosen.append(next_node.id)

    def repair(self):
        return


class Route(object):
    def __init__(self, node):
        self.start = node
        self.end = node
        self.path_nodes = [node]

    def fetch_next_nodes(self, cur_node):
        options = []
        for n in cur_node.neighbours:
            # TODO: Check if this works
            if n not in self.path_nodes:
                options.append(n)
        return options

    def reverse_route(self):
        # TODO: do we have to reverse path too?
        self.start, self.end = self.end, self.start

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
        # Create an array of routesets
        for i in range(num_routesets):
            self.routesets.append(
                RouteSet(
                    num_routes,
                    min_route_len,
                    max_route_len,
                    self.num_nodes)
            )

    def pick_best(self, parent, offspring):
        best_val = 0
        target = None

        # Finding the best route in parent wrt offspring
        for route in parent.routes:
            # Find the number of common nodes between the
            # selected route of parent and the offspring routeset
            common_nodes_len = len(set(list(map(lambda x: x.id, route.path_nodes)) + offspring.chosen))

            if common_nodes_len > 1:
                route_len = len(route.path_nodes)
                target_len = (route_len - common_nodes_len)/route_len
                if target_len > best_val:
                    target = route
                    best_val = target_len

        return target

    def crossover(self, parent1, parent2):
        pass


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
    travel_times = [[0] * size] * size
    # Signifies demand between two places
    demand = [[0] * size] * size

    with open('MandlTravelTimes.txt') as in_p2:
        i = 0
        for row in in_p2.readlines():
            # Input has blank rows in between - skipping them
            if not row.strip():
                continue

            for j, val in enumerate(row.split()):
                if val in ['Inf', '0']:
                    continue
                travel_times[i][j] = int(val)
                # TODO: Is it a better idea to just put the ID
                # Update neighbours of nodes - for nw putting the objects
                nodes[i].neighbours.append(nodes[j])
            i += 1

    with open('MandlDemand.txt') as in_p3:
        i = 0
        for row in in_p3.readlines():
            # Input has blank rows in between - skipping them
            if not row.strip():
                continue

            for j, val in enumerate(row.split()):
                if val in ['Inf', '0']:
                    continue
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
