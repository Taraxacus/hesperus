#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# gamestate.py:

from constants import *
from random import shuffle, choice

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

        # Initialize state variables
        self.dir_crossings = {crossing:None for crossing in CROSSINGS}
        self.dir_paths = {path:None for path in PATHS}
        self.dir_resources = {i:{resource:0 for resource in RESOURCES} for i in range(self.number_players)}
        self.dir_devcards = {i:0 for i in range(self.number_players)}
        self.dir_knights = {i:0 for i in range(self.number_players)}

        self.largest_army = (0, None)

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
        other_crossings = CROSSINGS - free_crossings
        return {crossing for crossing in free_crossings if all(not(vec_add(crossing, direction) in other_crossings) for direction in DIRECTIONS)}

    def pays(self, n, cost):
        if all(cost[resource] <= self.dir_resources[n][resource] for resource in RESOURCES):
            for resource in RESOURCES:
                self.dir_resources[n][resource] -= cost[resource]
            return True
        return False

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

    def number_resources(self, n):
        return sum(self.dir_resources[n].values())

    def adjacent_players(self, hexcoor):
        players = set()
        for direction in DIRECTIONS:
            crossing = vec_add(hexcoor, direction)
            piece = self.dir_crossings[crossing]
            if not piece == None:
                players.add(piece[1])
        return players

    def update_armies(self, n):
        self.dir_devcards[n] -= 1
        self.dir_knights[n] += 1
        if self.dir_knights[n] > self.largest_army[0]:
            self.largest_army = (self.dir_knights[n], n)

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
        return np.random.choice(list(resources.keys()), p=p)

    def print_state(self):
        for n in range(self.number_players):
            resources = self.dir_resources[n]
            devcards = self.dir_devcards[n]
            knights = self.dir_knights[n]
            vps = self.victory_points(n)
            print(f"Player {n}: Resources: {resources}; {devcards} devcards, {knights} knights, {vps} victory points.")

