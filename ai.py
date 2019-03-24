#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# ai.py:

from constants import *
from gamestate import GameState
from random import choice, randint

class AI:
    def __init__(self, number):
        self.number = number

    def check(self):
        return True

    def initial_settlement(self, game_state):
        crossing = choice(tuple(game_state.available_crossings()))
        path = choice(tuple(game_state.adjacent_paths(crossing)))
        return crossing, path
    
    def get_action(self, game_state):
        return "pass"

    def get_robbed(self, game_state):
        n = self.number
        l = game_state.number_resources(n)//2
        resources = RESOURCES.copy()
        while l > 0:
            resource = game_state.choose_resource_card(n)
            game_state.dir_resources[n][resource] -= 1
            l -= 1

    def set_robber(self, game_state):
        hexcoor = choice(HEXCOORS)
        players = game_state.adjacent_players(hexcoor)
        if players == set():
            player = None
        else:
            player = choice(tuple(players))
        return hexcoor, player

class AIRandom(AI):
    def get_action(self, game_state):
        n = self.number
        while True:
            r = randint(0,7)
            if r == 0:
                try:
                    path = choice(tuple(game_state.accessible_paths(n)))
                    s = []
                    for crossing in path:
                        for i in crossing:
                            s.append(str(i))
                    #print(n, game_state.dir_resources[n], path)
                    return "b r "+(" ".join(s))
                except Exception as e:
                    #print(e)
                    continue
            elif r == 1:
                try:
                    crossing = choice(tuple(game_state.accessible_crossings(n)))
                    s = []
                    for i in crossing:
                        s.append(str(i))
                    #print(n, game_state.dir_resources[n], crossing)
                    return "b s "+ (" ".join(s))
                except Exception as e:
                    #print(e)
                    continue
            elif r == 2:
                try:
                    crossing = choice(tuple(game_state.settlements_of(n)))
                    s = []
                    for i in crossing:
                        s.append(str(i))
                    #print(n, game_state.dir_resources[n], crossing)
                    return "b c "+ (" ".join(s))
                except Exception as e:
                    #print(e)
                    continue
            elif r == 3:
                return "b d"
            elif r == 4:
                return "p d"
            elif r == 5:
                try:
                    resource1 = choice(RESOURCES)
                    resource2 = choice(RESOURCES)
                    return f"t {resource1} {resource2}"
                except Exception as e:
                    #print(e)
                    continue
            return "pass"

class AICom(AIRandom):
    def __init__(self, number):
        self.number = number
        self.next_settlement = None
        self.next_city = None

    def best_settlement_location(self, game_state):#, initial_settlements=True):
        crossings = game_state.available_crossings()
        dir_points = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}

        best_points = 0
        best_crossings = set()
        for crossing in crossings:
            points = 0
            hexcoors = game_state.adjacent_hexcoors(crossing)
            for hexcoor in hexcoors:
                if hexcoor in game_state.dir_chips:
                    m = 1
                    if game_state.dir_hexes[hexcoor] in ["G", "O"]:
                        m = 1.5
                    points += m*dir_points[game_state.dir_chips[hexcoor]]
            if points == best_points:
                best_crossings.add(crossing)
            elif points > best_points:
                best_crossings = {crossing}
                best_points = points
        #print(best_crossings)
        return best_crossings

    def initial_settlement(self, game_state):
        crossing = choice(tuple(self.best_settlement_location(game_state)))
        path = choice(tuple(game_state.adjacent_paths(crossing)))
        #print(crossing, path)
        return crossing, path

class AIUser(AI):
    def check(self):
        input(f"You are player {self.number}. Press enter if you are ready. ")
        return True

    def initial_settlement(self, game_state):
        n = self.number
        while True:
            #raw_crossing = input("Where do you want to build your settlement? (Two numbers separated by space) ")
            raw_crossing = input(f"\nYou are player {n}. Where do you want to build your settlement? ")
            if raw_crossing == "r":
                crossing = choice(tuple(game_state.available_crossings()))
                break
            try:
                crossing = tuple([int(s) for s in raw_crossing.split()])
                if not crossing in game_state.available_crossings():
                    print("That is not an available crossing!")
                    raise Error
                break
            except Exception as e:
                print("Something failed!")
                print(e)
        while True:
            #raw_crossing2 = input("In the direction of which crossing do you want to build your road? (Two numbers separated by space) ")
            raw_crossing2 = input("\nIn the direction of which crossing do you want to build your road? ")
            if raw_crossing2 == "r":
                path = choice(tuple(game_state.adjacent_paths(crossing)))
                break
            try:
                crossing2 = tuple([int(s) for s in raw_crossing2.split()])
                path = frozenset({crossing, crossing2})
                if not path in game_state.adjacent_paths(crossing):
                    print("That is not an adjacent path!")
                    raise Error
                break
            except Exception as e:
                print("Something failed!")
                print(e)
        return crossing, path

    def get_action(self, game_state):
        n = self.number
        l, b, g, w, o = [game_state.dir_resources[n][resource] for resource in "LBGWO"]
        d = game_state.dir_devcards[n]
        k = game_state.dir_knights[n]
        #return input(f"\nYou are player {n}. You have {l} lumber, {b} bricks, {g} grain, {w} wool, {o} ore, {d} development cards and {k} knights.\n\
#What do you want to do? ")
        game_state.print_state()
        return input(f"You are player {n}. What do you want to do? ")
