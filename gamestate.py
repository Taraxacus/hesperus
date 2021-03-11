#!/usr/bin/python
    # Author: Maximilian Weinberg
# Date: 2019-03-24
# gamestate.py:

from random import shuffle, choice
from numpy.random import choice as npchoice

from constants import *

HEXES = 4*["L"] + 3*["B"] + 4*["G"] + 4*["W"] + 3*["O"] + ["D"]
SPIRALS = [[ 1, 2, 3, 7,12,16,19,18,17,13, 8, 4, 5, 6,11,15,14, 9,10],
           [ 3, 7,12,16,19,18,17,13, 8, 4, 1, 2, 6,11,15,14, 9, 5,10],
           [12,16,19,18,17,13, 8, 4, 1, 2, 3, 7,11,15,14, 9, 5, 6,10],
           [19,18,17,13, 8, 4, 1, 2, 3, 7,12,16,15,14, 9, 5, 6,11,10],
           [17,13, 8, 4, 1, 2, 3, 7,12,16,19,18,14, 9, 5, 6,11,15,10],
           [ 8, 4, 1, 2, 3, 7,12,16,19,18,17,13, 9, 5, 6,11,15,14,10],
          ]
CHIP_ORDERS = [[HEXCOORS[i-1] for i in spiral] for spiral in SPIRALS]
CHIPS = [ 5, 2, 6, 3, 8,10, 9,12,11, 4, 8,10, 9, 4, 5, 6, 3,11]
#CHIPS = list(range(19))

PORTS = RESOURCES + 4*["X"]

class GameState:
    def __init__(self, number_players, victory_points_to_win=10):
        self.number_players = number_players
        self.victory_points_to_win = victory_points_to_win

        # Randomize board
        hexes = HEXES.copy()
        shuffle(hexes)
        self.dir_hexes = dict(zip(HEXCOORS, hexes))

        chip_order = choice(CHIP_ORDERS)
        self.dir_chips = {}
        self.robber = None
        j = 0
        for coor in chip_order:
            if self.dir_hexes[coor] not in NO_YIELDS:
                self.dir_chips[coor] = CHIPS[j]
                j+=1
            else:
                self.robber = coor

        ports = PORTS.copy()
        shuffle(ports)
        self.dir_ports = dict(zip(PORTCOORS, ports))

        # Initialize state variables
        self.dir_crossings = {crossing:None for crossing in CROSSINGS}
        self.dir_paths = {path:None for path in PATHS}
        self.dir_resources = {i:{resource:0 for resource in RESOURCES} for i in range(self.number_players)}
        self.dir_devcards = {i:0 for i in range(self.number_players)}
        self.dir_knights = {i:0 for i in range(self.number_players)}

        self.largest_army = (0, None)

    # READ methods
    def are_adjacent_crossings(self, crossing1, crossing2):
        return (vec_diff(crossing1, crossing2) in DIRECTIONS)

    def are_adjacent_paths(self, path1, path2):
        return (not path1 & path2 == set())

    def are_adjacent_crossing_and_path(self, crossing, path):
        return (crossing in path)

    def adjacent_paths(self, crossing):
        paths = set()
        for direction in DIRECTIONS:
            point = vec_add(crossing, direction)
            if point in CROSSINGS:
                paths.add(frozenset({crossing, point}))
        return paths

    def adjacent_crossings(self, crossing):
        crossings = set()
        for direction in DIRECTIONS:
            point = vec_add(crossing, direction)
            if point in CROSSINGS:
                crossings.add(point)
        return crossings

    def adjacent_hexcoors(self, crossing):
        hexcoors = set()
        for direction in DIRECTIONS:
            point = vec_add(crossing, direction)
            if point in HEXCOORS:
                hexcoors.add(point)
        return hexcoors

    def free_crossings(self):
        return {crossing for crossing in self.dir_crossings if self.dir_crossings[crossing] is None}

    def free_paths(self):
        return {path for path in self.dir_paths if self.dir_paths[path] is None}

    def available_crossings(self):
        free_crossings = self.free_crossings()
        #if CROSSINGS == free_crossings:
            #return free_crossings
        other_crossings = CROSSINGS - free_crossings
        #print(other_crossings)
        return {crossing for crossing in free_crossings if all(not(vec_add(crossing, direction) in other_crossings) for direction in DIRECTIONS)}

    def network(self, n):
        network = set()
        for path in self.dir_paths:
            if self.dir_paths[path] == n:
                #network |= path
                for crossing in path:
                    if self.dir_crossings[crossing] == None:
                        network.add(crossing)
                    elif self.dir_crossings[crossing][1] == n:
                        network.add(crossing)
        return network

    def accessible_crossings(self, n):
        return self.available_crossings() & self.network(n)

    def accessible_paths(self,n):
        free_paths = self.free_paths()
        return {path for path in free_paths if any(crossing in path for crossing in self.network(n))}

    def paths_of(self, n):
        return {path for path in self.dir_paths if self.dir_paths[path] == n}

    def settlements_of(self, n):
        return {crossing for crossing in self.dir_crossings if self.dir_crossings[crossing] == (1,n)}

    def cities_of(self, n):
        return {crossing for crossing in self.dir_crossings if self.dir_crossings[crossing] == (2,n)}

    def has_largest_army(self, n):
        return self.largest_army[0] == n

    def number_resources(self, n):
        return sum(self.dir_resources[n].values())

    def can_afford(self, n, cost):
        return all(cost[resource] <= self.dir_resources[n][resource] for resource in RESOURCES)

    def adjacent_players(self, hexcoor):
        players = set()
        for direction in DIRECTIONS:
            crossing = vec_add(hexcoor, direction)
            piece = self.dir_crossings[crossing]
            if not piece == None:
                players.add(piece[1])
        return players

    def price(self, n, resource):
        price = 4
        for port in PORTCOORS:
            if self.dir_ports[port] == resource:
                for crossing in port:
                    if self.dir_crossings[crossing] in [(1,n), (2,n)]:
                        return 2
            elif self.dir_ports[port] == "X":
                for crossing in port:
                    if self.dir_crossings[crossing] in [(1,n), (2,n)]:
                        price = 3
        return price

    def victory_points(self, n):
        vps = 0
        for crossing in self.dir_crossings:
            if self.dir_crossings[crossing] == (1, n):
                vps += 1
            if self.dir_crossings[crossing] == (2, n):
                vps += 2
        if self.largest_army[1] == n:
            vps += 2
        return vps

    def has_won(self, n):
        return (self.victory_points(n) >= self.victory_points_to_win)

    def choose_resource_card(self, n):
        m = self.number_resources(n)
        resources = self.dir_resources[n]
        if m == 0:
            return None
        p = [(resources[resource]/m) for resource in resources]
        #return np.random.choice(list(resources.keys()), p=p)
        return npchoice(list(resources.keys()), p=p)

    def print_state(self):
        for n in range(self.number_players):
            resources = self.dir_resources[n]
            devcards = self.dir_devcards[n]
            knights = self.dir_knights[n]
            vps = self.victory_points(n)
            #resource_string = ""
            #for resource in resources:
                #resource_string += resources[resource] * (resource + " ")
            print(f"Player {n}: Resources: {resources}; {devcards} devcards, {knights} knights, {vps} victory points.")

    # WRITE methods
    def pays(self, n, cost):
        if self.can_afford(n, cost):
            for resource in RESOURCES:
                self.dir_resources[n][resource] -= cost[resource]
            return True
        return False

    def update_armies(self, n):
        self.dir_devcards[n] -= 1
        self.dir_knights[n] += 1
        if self.dir_knights[n] > max(self.largest_army[0],2):
            self.largest_army = (self.dir_knights[n], n)

    def update_roads(self, n, path=None):
        if path == None:
            # Insert full algorithm here
            pass
        else:
            for crossing1 in path:
                m = 0
                if self.dir_crossings[crossing1] != None:
                    if self.dir_crossings[crossing1][1] != n:
                        m = 1
                if m == 0:
                    for direction in DIRECTIONS:
                        crossing2 = vec_add(crossing1, direction)
                        path2 = frozenset({crossing1, crossing2})
                        if path2 in PATHS:
                            if self.dir_paths[path2] == n:
                                m += 1
                if m == 1:
                    # crossing1 is an end
                    # Count longest road starting at crossing1
                    pass
                    return
            # Both crossing1 and crossing2 are connected to roads
            # Call full counting algorithm

    ### Actions
    def build_initial_settlement(self, n, crossing, path):
        if crossing in self.available_crossings():
            if self.are_adjacent_crossing_and_path(crossing, path):
                self.dir_crossings[crossing] = (1,n)
                self.dir_paths[path] = n
                return 0
            else:
                return 2
        else:
            return 1
    def build_road(self, n, path):
        if path in self.accessible_paths(n):
            cost = PRICES["road"]
            if self.pays(n, cost):
                self.dir_paths[path] = n
                return 0
            else:
                return 1
        else:
            return 2

    def build_settlement(self, n, crossing):
        if crossing in self.accessible_crossings(n):
            cost = PRICES["settlement"]
            if self.pays(n, cost):
                self.dir_crossings[crossing] = (1,n)
                return 0
            else:
                return 1
        else:
            return 2

    def build_city(self, n, crossing):
        if crossing in self.settlements_of(n):
            cost = PRICES["city"]
            if self.pays(n, cost):
                self.dir_crossings[crossing] = (2,n)
                return 0
            else: #elif not DEBUG:
                return 1
        else:
            return 2

    def buy_devcard(self, n):
        cost = PRICES["devcard"]
        if self.pays(n, cost):
            self.dir_devcards[n] += 1
            return 0
        else:
            return 1
