#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-10
# actor.py: A manual AI for this Catan simulation

from random import choice

from constants import *
from player import AI, dict_ai
#import tensorflow as tf

# For testing
from ui import GuiTurtle
from game import run

#class GuiTest(GuiTurtle):
    #pass
    #def ask_player_type(self, number, dict_ai):
        #pass

#class Actor(AI):
    #pass

class AIKnight(AI):
    def __init__(self, number):
        self.number = number
        self.preferences = {"L":10, "B":10, "G":30, "W":10, "O":35, "D":0}
        self.dir_points = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        self.distance_multiplier = 60

        self.name = f"Knight {number}"

    def best_settlement_location(self, game_state, mode=0):
        if mode == 2:
            crossings = game_state.settlements_of(self.number)
        else:
            crossings = game_state.available_crossings()
        if len(crossings) == 0:
            return set()
        dir_points = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}

        best_points = -2000
        best_crossings = set()
        for crossing in crossings:
            points = 0
            hexcoors = game_state.adjacent_hexcoors(crossing)
            for hexcoor in hexcoors:
                #if hexcoor in game_state.dir_chips:
                    #m = 1
                    #if game_state.dir_hexes[hexcoor] in ["G", "O"]:
                        #m = 1.5
                    #points += m*dir_points[game_state.dir_chips[hexcoor]]
                hexx = game_state.dir_hexes[hexcoor]
                m = self.preferences[hexx]
                if hexcoor in game_state.dir_chips:
                    points += m*dir_points[game_state.dir_chips[hexcoor]]
                #print(hexcoor,hexx,m,points)
            if hexcoor in PORTCOORS2:
                points += 80
            if mode == 1:
                distance = self.get_distance(game_state, crossing)
                if distance == -1:
                    points = -2001
                else:
                    points -= self.distance_multiplier*distance

            if points == best_points:
                resources = [game_state.dir_hexes[hexcoor] for hexcoor in hexcoors]
                #print(crossing, resources, points)
                #input()
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

    def get_distance(self, game_state, settlement_location, give_path=False):
        #print(type(settlement_location))
        network = game_state.network(self.number)
        if settlement_location in network:
            if give_path:
                return
            return 0
        crossings = [(settlement_location, 0)]
        distance = -1
        for tuple_crossing in crossings:
            crossing1, d = tuple_crossing
            if d>5:
                break
            for crossing2 in game_state.adjacent_crossings(crossing1):
                if not (game_state.dir_paths[frozenset({crossing1, crossing2})] == None):
                    continue
                #print(type(crossing1), type(crossing2))
                if not crossing2 in crossings:
                    #crossings[crossing2] = crossings[crossing1]+1
                    crossings.append((crossing2, d+1))
                if crossing2 in network:
                    distance = d+1
                    if give_path:
                        path = frozenset({crossing1, crossing2})
                    break
            if not distance == -1:
                break
        if give_path:
            if distance == -1:
                return None
            return path
        return distance

    def get_action(self, game_state):
        print(self.name, "is thinking...")
        resources = game_state.dir_resources[self.number]
        print("Victory points:", game_state.victory_points(self.number))
        print(resources)

        build_settlement = False
        build_road = False
        build_city = False
        #buy_devcard = False

        settlements = self.best_settlement_location(game_state, 1)
        if not len(settlements) == 0:
            next_settlement = choice(tuple(settlements))
            next_path = self.get_distance(game_state, next_settlement, True)
            if next_path == None:
                build_settlement = True
            else:
                build_road = True

        cities = self.best_settlement_location(game_state, 2)
        if not len(cities) == 0:
            next_city = choice(tuple(cities))
            build_city = True
            
        buy_devcard = (game_state.victory_points(self.number)>=5)
        buy_devcard &= not game_state.has_largest_army(self.number)
        buy_devcard &= not build_city
        
        play_devcard = game_state.dir_devcards[self.number] > 0

        cost_settlement = {"L":1, "B":1, "G":1, "W":1, "O":0}
        build_settlement &= game_state.can_afford(self.number, cost_settlement)
        cost_city = {"L":0, "B":0, "G":2, "W":0, "O":3}
        build_city &= game_state.can_afford(self.number, cost_city)
        cost_road = {"L":1, "B":1, "G":0, "W":0, "O":0}
        build_road &= game_state.can_afford(self.number, cost_road)
        cost_devcard = {"L":0, "B":0, "G":1, "W":1, "O":1}
        buy_devcard &= game_state.can_afford(self.number, cost_devcard)

        command = "pass"
        if play_devcard:
            input(f"{self.number} plays a devcard!")
            command = "p d"
        elif build_settlement:
            s = []
            for i in next_settlement:
                s.append(str(i))
            command = "b s "+ (" ".join(s))
            input(f"{self.name} will build a settlement at {s}.")
        elif build_city:
            s = []
            for i in next_city:
                s.append(str(i))
            command = "b c "+ (" ".join(s))
            input(f"{self.name} will build a city at {s}.")
        elif build_road:
            s = []
            for crossing in next_path:
                for i in crossing:
                    s.append(str(i))
            command = "b r "+ (" ".join(s))
        elif buy_devcard:
            #input("{self.number} buys devcard!")
            command = "b d"
        else:
            # TODO Handeln?
            sellables = {resource for resource in RESOURCES if resources[resource] >= game_state.price(self.number, resource)}
            if len(sellables) != 0:
                buyables = {resource for resource in RESOURCES if resources[resource] == 0}
                buyables -= {"W"} # Never trade for wool. Just don't.
                if len(buyables) == 0:
                    buyables = {"G", "O"} - sellables
                if len(buyables) == 0:
                    input(f"THIS IS A RARE CASE!\nResources: {resources}\nSettlement: {settlements}")
                    #buyables = {resources for resource in RESOURCES if not (resource in sellables)}
                    buyables = {"W"}
                resource1 = choice(tuple(sellables))
                resource2 = choice(tuple(buyables))
                command = f"t {resource1} {resource2}"

        print(self.number, "does:", command)
        #input("Continue? ")
        return command

class AITraveller(AIKnight):
    def __init__(self, number):
        self.number = number
        self.preferences = {"L":28, "B":28, "G":19, "W":6, "O":19, "D":0}
        self.dir_points = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        self.distance_multiplier = 35

        self.name = f"Traveller {number}"

class AIIndie(AIKnight):
    def __init__(self, number):
        self.number = number
        self.preferences = {"L":24, "B":24, "G":22, "W":8, "O":22, "D":0}
        self.dir_points = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        self.distance_multiplier = 45

        self.name = f"Indie {number}"

dict_ai["knight"] = AIKnight
dict_ai["traveller"] = AITraveller
dict_ai["indie"] = AIIndie

def main():
    gui = GuiTurtle()
    gui.intro()
    
    players = gui.ask_players(dict_ai)
    run(gui, players)

    input("That's it!")

if __name__=="__main__":
    main()
