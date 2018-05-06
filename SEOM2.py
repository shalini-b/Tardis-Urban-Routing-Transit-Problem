import random
import copy


class Node(object):
    def __init__(self, id, posx, posy):
        self.id = id
        self.posx = posx
        self.posy = posy
        self.neighbours = []


class RouteSet(object):
    def __init__(self):
        self.num_routes = num_routes
        self.min_route_len = min_route_len
        self.max_route_len = max_route_len
        self.shortest_path_times = copy.deepcopy(travel_times)
        self.num_nodes = len(nodes)
        # Contains IDs of chosen nodes till now
        self.chosen = set()
        # Contains route objects for this routeset
        self.routes = []
        # Maintains a map of node & routes it is present in
        self.node_map = {}
        self.passenger_cost = 0
        self.operator_cost = 0

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

    def compute_passenger_cost(self):
        numerator = 0
        denominator = 1
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                numerator += (demand[i][j] * self.shortest_path_times[i][j])
                denominator += demand[i][j]

        self.passenger_cost = numerator/denominator

    def compute_operator_cost(self):
        _sum = 0
        for route in self.routes:
            for i in range(len(route.path_nodes) - 1):
                _sum += self.shortest_path_times[i][i+1]
        self.operator_cost = _sum

    def recalculate_chosen_nodes(self):
        self.chosen = set()
        self.chosen.update([node.id for route in self.routes for node in route.path_nodes])

    def update_connecting_nodes(self, cur_route, target_node):
        # If it is already part of another route
        if self.node_map.get(target_node.id):
            # Add it as a connecting node to present route
            cur_route.connecting_nodes.append(target_node)
            # Add this node as connecting node in other
            # common routes if not present
            for r in self.node_map[target_node.id]:
                if target_node in r.connecting_nodes:
                    continue
                r.connecting_nodes.append(target_node)

    def generate_routeset(self):
        # Create a route on every iteration
        for count in range(self.num_routes):
            # Select random size for route
            route_len = random.randrange(self.min_route_len, self.max_route_len + 1)

            if count == 0:
                # Select the starting node for the first route
                cur_node = nodes[random.randrange(size)]
                # Create route
                route = Route(cur_node)
            else:
                # Select the starting node for an adjoining route
                # from the list of chosen nodes to ensure connectivity
                cur_node = nodes[random.choice(list(self.chosen)) - 1]
                # Create route
                route = Route(cur_node)
                # Update the connecting nodes for all routes related to node
                self.update_connecting_nodes(route, cur_node)

            # Update node map and chosen with new route and node
            self.node_map.setdefault(cur_node.id, []).append(route)
            self.chosen.add(cur_node.id)
            # Add to routes
            self.routes.append(route)

            route_reversed = False
            # Add nodes till route_len is satisfied
            while len(route.path_nodes) < route_len:
                # Get potential neighbours
                next_nodes = route.fetch_next_nodes(cur_node)
                if not next_nodes:
                    # Try reversing the route & add nodes
                    if not route_reversed:
                        route.reverse_route()
                        route_reversed = True
                    else:
                        # Adding at both ends tested, leave
                        break
                else:
                    next_node = random.choice(next_nodes)
                    route.append_to_path_end(next_node)

                    # Update the connecting nodes for all routes
                    # related to node if applicable
                    self.update_connecting_nodes(route, next_node)

                    # Update node map and chosen with new route and node
                    self.node_map.setdefault(next_node.id, []).append(route)
                    self.chosen.add(next_node.id)
                    cur_node = next_node

        # If routeset does not have all the required nodes
        if len(self.chosen) < self.num_nodes:
            # Try adding nodes to different paths by repairing
            self.repair()
            # Even if repair does not work, fail
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
            if len(routes_checked) == num_routes:
                break

            self._add_nodes(routes_checked)
            count -= 1

    def _add_nodes(self, routes_checked):
        # Select the route not checked till now
        cnt = 0
        rand_route = self.routes[random.randrange(num_routes)]
        while rand_route in routes_checked and cnt < num_routes:
            cnt += 1
            rand_route = self.routes[random.randrange(num_routes)]

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
                rand_route.append_to_path_end(next_node)

                # Update the connecting nodes for all routes
                # related to node if applicable
                self.update_connecting_nodes(rand_route, next_node)

                self.node_map.setdefault(next_node.id, []).append(rand_route)
                self.chosen.add(next_node.id)

    def delete_nodes(self):
        # Choose a random number of nodes to delete
        count = random.randrange(1, (self.max_route_len * self.num_routes) // 2)

        routes_checked = []
        while count > 0:
            # Check if all routes are exhausted for removal
            if len(routes_checked) == self.num_routes:
                break

            # Select the route not checked till now
            cnt = 0
            rand_route = self.routes[random.randrange(self.num_routes)]
            while rand_route in routes_checked and cnt < num_routes:
                cnt += 1
                rand_route = self.routes[random.randrange(self.num_routes)]

            # Append it to routes checked
            routes_checked.append(rand_route)

            # Add nodes at the end/start of the route if possible
            route_reversed = False
            # Checking if the length of route is greater than
            # min_route_len mentioned by user
            while len(rand_route.path_nodes) > self.min_route_len:
                if not self.check_for_node_deletion(rand_route):
                    # Reverse the route & try adding at the start
                    if not route_reversed:
                        rand_route.reverse_route()
                        route_reversed = True
                    else:
                        # Adding at both ends tested, leave
                        break
                else:
                    # remove route from node map
                    # NOTE: we do not need to remove from chosen
                    self.node_map[rand_route.end.id].remove(rand_route)

                    rand_route.connecting_nodes.remove(rand_route.end)
                    target_paths = self.node_map[rand_route.end.id]
                    if target_paths == 1:
                        target_paths[0].connecting_nodes.remove(rand_route.end.id)

                    # Safely delete the end node
                    rand_route.delete_from_path_end()

            count -= 1

    def check_for_node_deletion(self, route):
        # Check if the node at route end is duplicated and can be
        # removed without breaking the connectivity of routeset
        target_paths = self.node_map[route.end.id]
        if len(target_paths) <= 1:
            # No duplicates
            return False

        if any(map(lambda x: len(x.connecting_nodes) <= 1, target_paths)):
            # The end node of this route is the only connection some
            # other path has to the rest of the graph
            return False

        return True

    def swap_routes(self, routeset_to_add, target_route):
        # Add target_route from current one to routeset_to_add
        routeset_to_add.routes.append(target_route)
        for _node in target_route.path_nodes:
            self.update_connecting_nodes(target_route, _node)
            routeset_to_add.node_map.setdefault(_node.id, []).append(target_route)
        routeset_to_add.chosen.update(map(lambda x: x.id, target_route.path_nodes))

        # Remove target_route from current one
        self.routes.remove(target_route)
        self.recalculate_chosen_nodes()

    def repair(self):
        routes_checked = []
        while len(self.chosen) < self.num_nodes:
            # Check if all routes are exhausted for addition
            if len(routes_checked) == len(self.routes):
                break

            self._add_nodes(routes_checked)

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
        self.compute_operator_cost()
        self.compute_passenger_cost()

    def mutate(self):
        rand = random.randrange(10)
        if rand % 2 == 1:
            self.add_nodes()
        else:
            # self.add_nodes()
            self.delete_nodes()


class Route(object):
    def __init__(self, node):
        self.start = node
        self.end = node
        # Contains connecting nodes to other paths
        self.connecting_nodes = []
        # Describes the sequence of node in path
        self.path_nodes = [node]

    @property
    def hashed_id(self):
        # Unique ID for the route to identify different variations of it
        return sum(map(lambda x: x.id, self.path_nodes))

    def fetch_next_nodes(self, cur_node):
        options = []
        for n in cur_node.neighbours:
            if n not in self.path_nodes:
                options.append(n)
        return options

    def reverse_route(self):
        self.start, self.end = self.end, self.start
        self.path_nodes.reverse()

    def append_to_path_end(self, node):
        self.path_nodes.append(node)
        self.end = node

    def delete_from_path_end(self):
        self.path_nodes.pop()
        self.end = self.path_nodes[-1]


class TransitGraph(object):
    def __init__(self):
        self.routesets = []

    def create_initial_population(self):
        # Create an array of routesets
        count = 0
        while count < num_routesets:
            sample_rs = RouteSet()
            if sample_rs.generate_routeset():
                self.routesets.append(sample_rs)
                count += 1

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
        offspring = RouteSet()

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
                best_route = self.pick_best(p2, offspring)
                cnt = 0
                while best_route in offspring.routes and cnt <= 100:
                    cnt += 1
                    best_route = self.pick_best(p2, offspring)
                if cnt == 100:
                    return offspring

                if best_route:
                    # Remove best_route from parent2 and add to offspring
                    p2.swap_routes(offspring, best_route)
            else:
                # Pick the best route available in P2
                # which is not present in offspring yet
                best_route = self.pick_best(p1, offspring)
                cnt = 0
                while best_route in offspring.routes and cnt <= 100:
                    cnt += 1
                    best_route = self.pick_best(p1, offspring)
                if cnt == 100:
                    return offspring

                if best_route:
                    # Remove best_route from parent1 and add to offspring
                    p1.swap_routes(offspring, best_route)

        return offspring


if __name__ == '__main__':
    # List of node objects
    # NOTE: Do not change the order of nodes in this list
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

    # Create travel times matrix from one node to another
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
                if val != 9999:
                    # Update neighbours of nodes - for nw putting the objects
                    nodes[i].neighbours.append(nodes[j])
            i += 1

    # Create demand matrix from one node to another
    with open('MandlDemand.txt') as in_p3:
        i = 0
        for row in in_p3.readlines():
            # Input has blank rows in between - skipping them
            if not row.strip():
                continue

            for j, val in enumerate(row.split()):
                if val == 'Inf':
                    val = 9999
                if val != 9999:
                    demand[i][j] = int(val)
            i += 1

    # Number of routeset combinations
    num_routesets = int(input('Number of routesets: '))
    # Number of routes in each routeset
    num_routes = int(input('Number of routes in each routeset: '))
    # Maximum and minimum number of routes in route set
    min_route_len, max_route_len = list(map(int, input('Input minimum and maximum route length: ').split()))

    # Create initial population of routesets
    transit_map = TransitGraph()
    transit_map.create_initial_population()

    # Find minimum values of passenger cost and operator cost
    # Find their corresponding routesets
    min_cp = 99999999
    min_co = 99999999
    min_cp_rt = None
    min_co_rt = None
    for rs in transit_map.routesets:
        rs.generate_shortest_path_pairs()
        if rs.operator_cost < min_cp:
            min_cp_rt = rs
            min_cp = rs.passenger_cost
        if rs.operator_cost < min_co:
            min_co_rt = rs
            min_co = rs.operator_cost

    runThis = True
    # TODO: Limit this loop?
    while runThis:
        runThis = False
        for rs_index in range(num_routesets):
            Parent1 = transit_map.routesets[rs_index]

            # Choose random parent2
            p2_id = random.randrange(num_routesets)
            while p2_id == rs_index:
                p2_id = random.randrange(num_routesets)

            # Create offspring
            Parent2 = transit_map.routesets[p2_id]
            offspring = transit_map.crossover(Parent1, Parent2)
            offspring.mutate()

            # Validate offspring
            if len(offspring.chosen) < offspring.num_nodes:
                offspring.repair()
                if len(offspring.chosen) < offspring.num_nodes:
                    continue

            for op in offspring.routes:
                print([j.id for j in op.path_nodes])
            print('----------')
            # Calculate passenger & operator costs
            offspring.generate_shortest_path_pairs()

            # Check if such a Routeset already exists
            flag = False
            for k in transit_map.routesets:
                if k == offspring:
                    flag = True
                    break
            if flag:
                # Create another offspring
                continue

            # Check if offspring is better than any of the parents
            # If yes, replace them and start over
            if Parent1.operator_cost > offspring.operator_cost and \
                    Parent1.passenger_cost > offspring.passenger_cost:
                transit_map.routesets[rs_index] = offspring
                runThis = True
                continue
            if Parent2.operator_cost > offspring.operator_cost and \
                    Parent2.passenger_cost > offspring.passenger_cost:
                transit_map.routesets[p2_id] = offspring
                runThis = True
                continue

            # Update the minimum values of operator cost & passenger
            # cost wrt offspring
            if offspring.operator_cost < min_co_rt.operator_cost:
                min_co_rt = offspring
                if Parent1 != min_cp_rt:
                    transit_map.routesets[rs_index] = offspring
                else:
                    transit_map.routesets[p2_id] = offspring
                runThis = True
                continue
            if offspring.passenger_cost < min_cp_rt.passenger_cost:
                min_cp_rt = offspring
                if Parent1 != min_co_rt:
                    transit_map.routesets[rs_index] = offspring
                else:
                    transit_map.routesets[p2_id] = offspring
                runThis = True
                continue

            # If the offspring values are same as that of any of the parent's values,
            # check if any other routeset can be replaced with offspring
            if any(map(lambda x: x.operator_cost == offspring.operator_cost and
                    x.passenger_cost == offspring.passenger_cost, [Parent1, Parent2])):
                for k in range(num_routesets):
                    temp = transit_map.routesets[k]
                    if temp.operator_cost > offspring.operator_cost and \
                            temp.passenger_cost > offspring.passenger_cost:
                        transit_map.routesets[k] = offspring
                        runThis = True
                        break

    print("Best passenger Cost:")
    for i in min_cp_rt.routes:
        print([j.id for j in i.path_nodes])
    print(min_cp_rt.passenger_cost)
    print("Best operator Cost:")
    for i in min_co_rt.routes:
        print([j.id for j in i.path_nodes])
    print(min_co_rt.operator_cost)
