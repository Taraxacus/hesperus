#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2017-07-01
# hesperus.py: Versuch einer Simulation von Die Siedler von Catan um spaeter
#       eine AI zu implementieren.

### Some general remarks:
###
### Use underscores, not camel case!
###
### Coordinates of vectors are given by tuples of length two.
### The vector (1,0) points straight upwards.
### The vector (0,1) points right and downwards, 120 degrees to the first vector.
### Both basis vectors have length specified by the HEX_LENGTH variable below.
###
### Abbreviations:
### L - lumber
### B - brick
### G - grain
### W - wool
### O - ore
### D - desert


from math import cos, sin, pi
import numpy as np
from random import randint, shuffle, choice
import time

from turtle import Turtle, Screen

COORDINATE_MATRIX1 = np.matrix([[0, 1], [cos(pi/6), -1/2]])
COORDINATE_MATRIX2 = np.linalg.inv(COORDINATE_MATRIX1)

COMONLY = False
DEBUG = False

RADIUS = 300
HOUSE  = 50
STAR   = 30
COLORS = {"sky":(0,0,0.3),
          "ground":(0,0,0),
          "star":(1,1,0.5),
          "road":(0.7,0.4,0.1),
          "sea":(0.8, 0.9, 1),
          "robber":(0.2, 0.1, 0),

          "player0":(0.1,0.1,0.8),
          "player1":(0.8,0,0),
          "player2":(1,0.6,0),
          "player3":(1,1,1),

          "pink":(1,0.3,0.7),
          "L":(  0, 0.4,   0),
          "B":(0.9, 0.4, 0.1),
          "G":(  1, 0.9, 0.1),
          "W":(0.6,   1, 0.4),
          "O":(0.4, 0.4, 0.4),
          "D":(  1, 0.9, 0.5),
         }
HEX_LENGTH = 60

HEXCOORS = [[ 2,-2], [ 3, 0], [ 4, 2],
        [ 0,-3], [ 1,-1], [ 2, 1], [ 3, 3],
    [-2,-4], [-1,-2], [ 0, 0], [ 1, 2], [ 2, 4],
        [-3,-3], [-2,-1], [-1, 1], [ 0, 3],
            [-4,-2], [-3, 0], [-2, 2]]
HEXCOORS = [tuple(i) for i in HEXCOORS]
#HEXCOORS_MAT = [np.matrix(coor) for coor in HEXCOORS]
DIRECTIONS = [[1,0], [1, 1], [0,1], [-1,0], [-1,-1], [0,-1]]
DIRECTIONS = [tuple(i) for i in DIRECTIONS]

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
NO_YIELDS = ["D"]
#CHIP_FONT = [2:("Arial", 8, "normal"),
RESOURCES = ["L", "B", "G", "W", "O"]

PRICES = {"settlement":{"L":1, "B":1, "G":1, "W":1, "O":0},
        "road":{"L":1, "B":1, "G":0, "W":0, "O":0},
        "city":{"L":0, "B":0, "G":2, "W":0, "O":3},
        "devcard":{"L":0, "B":0, "G":1, "W":1, "O":1}}

def roll_dice():
    return randint(1,6)+randint(1,6)

def vec_add(v1,v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def cart2hex(v):
    return 1/HEX_LENGTH * (np.matrix(v) * COORDINATE_MATRIX2)

def hex2cart(u):
    r = (HEX_LENGTH * (u*COORDINATE_MATRIX1)).tolist()
    # r is now a list containing exactly one list.
    r = tuple(r[0])
    return r

CROSSINGS = set()
for hexcoor in HEXCOORS:
    for direction in DIRECTIONS:
        CROSSINGS.add(vec_add(hexcoor,direction))

PATHS = set()
for crossing in CROSSINGS:
    for direction in DIRECTIONS:
        point = vec_add(crossing, direction)
        if point in CROSSINGS:
            PATHS.add(frozenset({crossing, point}))

#def leq(resources1, resources2):
    #return all(resources1[resource] <= resources2[resource] for resource in RESOURCES)

##################
#   GAME CLASS   #
##################


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
        return {crossing for crossing in self.dir_crossings if self.dir_crossings[crossing] == None}

    def free_paths(self):
        return {path for path in self.dir_paths if self.dir_paths[path] == None}

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


####################
#   RUN FUNCTION   #
####################

def run(gui):
    # Initialize players
    if not DEBUG:
        number_players = gui.ask_number_players()
    else:
        number_players = 4
    players = []
    for n in range(number_players):
        AIClass = gui.ask_player_type(n, [AI, AIRandom, AIUser])
        players.append(AIClass(n))

    game_state = GameState(number_players)
    gui.draw_board(game_state)

    # Check on players (is this useless?)⎈
    for player in players:
        if not player.check():
            return False

    # Initial settlements
    beginner = randint(0, game_state.number_players-1)
    for i in range(number_players):
        n = (beginner+i)%number_players
        crossing, path = players[n].initial_settlement(game_state)
        game_state.dir_crossings[crossing] = (1,n)
        game_state.dir_paths[path] = n
        gui.draw_board(game_state)
        gui.print(f"Player {n} build a settlement at {crossing}.")
        gui.print(f"Player {n} build a road at {path}.")
    for i in reversed(range(number_players)):
        n = (beginner+i)%number_players
        crossing, path = players[n].initial_settlement(game_state)
        game_state.dir_crossings[crossing] = (1,n)
        game_state.dir_paths[path] = n
        gui.print(f"Player {n} build a settlement at {crossing}.")
        gui.print(f"Player {n} build a road at {path}.")
        for hexcoor in game_state.adjacent_hexcoors(crossing):
            hexx = game_state.dir_hexes[hexcoor]
            if not hexx in NO_YIELDS:
                game_state.dir_resources[n][hexx] += 1
        gui.draw_board(game_state)
    gui.print(game_state.dir_resources)

    # Actual game loops
    n = beginner
    turn = 0
    running = True
    winner = None
    #if input("Pause...") in ("q", "quit"):
        #running = False
    while running:
        turn += 1

        if not DEBUG:
            gui.draw_board(game_state)
        if turn%number_players ==0:
            roundd = turn//number_players
            if roundd == 1000:
                running = False
            else:
                gui.print(f"We're going into round {roundd}!")

        # Dice roll
        w = roll_dice()
        gui.print(f"Player {n} rolled a {w}.")

        if w == 7:
            # Robber
            for n in range(number_players):
                hand = game_state.number_resources(n)
                if hand > 7:
                    players[n].get_robbed(game_state)
                    if not game_state.number_resources(n) == (hand - hand//2):
                        gui.print("Player {n} cheated the robber!")
            hexcoor, player = players[n].set_robber(game_state)
            game_state.robber = hexcoor
            if not player == None:
                resource = game_state.choose_resource_card(player)
                if not resource == None:
                    game_state.dir_resources[player][resource] -= 1
                    game_state.dir_resources[n][resource] += 1
            gui.draw_board(game_state)
        else:
            # Resources
            for hexcoor in HEXCOORS:
                resource = game_state.dir_hexes[hexcoor]
                if (not resource in NO_YIELDS) and (not game_state.robber == hexcoor):
                    if game_state.dir_chips[hexcoor] == w:
                        for direction in DIRECTIONS:
                            crossing = vec_add(hexcoor, direction)
                            piece = game_state.dir_crossings[crossing]
                            if not (piece == None):
                                if piece[0] == 1:
                                    game_state.dir_resources[piece[1]][resource] += 1
                                if piece[0] == 2:
                                    game_state.dir_resources[piece[1]][resource] += 2

        # Turn of player n
        player = players[n]
        while True:
            action = player.get_action(game_state)
            list_action = action.split(" ")
            command = list_action[0]

            # Command pass
            if command == "pass":
                if game_state.has_won(n):
                    winner = n
                    running = False
                break

            # Command quit
            elif command in ("q", "quit"):
                running = False
                break

            # Command debug
            elif command == "debug":
                #print(game_state.dir_resources)
                game_state.print_state()

            # Command trade
            elif command in ("t", "trade"):
                try:
                    resource1 = list_action[1]
                    resource2 = list_action[2]
                    cost = {resource:0 for resource in RESOURCES}
                    cost[resource1] += 4
                    if game_state.pays(n, cost):
                        game_state.dir_resources[n][resource2] += 1
                    elif not DEBUG:
                        gui.print("You cannot afford to do that!")
                except:
                    print("Something failed!")

            # Command build/buy
            elif command in ("b", "build", "buy"):
                arg = list_action[1]
                if arg in ("r", "road"):
                    try:
                        crossing1 = (int(list_action[2]), int(list_action[3]))
                        crossing2 = (int(list_action[4]), int(list_action[5]))
                        path = frozenset({crossing1, crossing2})
                        if path in game_state.accessible_paths(n):
                            cost = PRICES["road"]
                            if game_state.pays(n, cost):
                                game_state.dir_paths[path] = n
                                gui.print(f"Player {n} build a road at {path}.")
                            elif not DEBUG:
                                gui.print("You cannot afford to do that!")
                        else:
                            gui.print("That is not an accessible path location!")
                    except Exception as e:
                        print("Something failed!")
                        print(e)
                if arg in ("s", "settlement"):
                    try:
                        crossing = (int(list_action[2]), int(list_action[3]))
                        if crossing in game_state.accessible_crossings(n):
                            cost = PRICES["settlement"]
                            if game_state.pays(n, cost):
                                game_state.dir_crossings[crossing] = (1,n)
                                gui.print(f"Player {n} build a settlement at {crossing}.")
                            elif not DEBUG:
                                gui.print("You cannot afford to do that!")
                        else:
                            gui.print("That is not an accessible settlement location!")
                    except Exception as e:
                        print("Something failed!")
                        print(e)
                if arg in ("c", "city"):
                    try:
                        crossing = (int(list_action[2]), int(list_action[3]))
                        if crossing in game_state.settlements_of(n):
                            cost = PRICES["city"]
                            if game_state.pays(n, cost):
                                game_state.dir_crossings[crossing] = (2,n)
                                gui.print(f"Player {n} build a city at {crossing}.")
                            elif not DEBUG:
                                gui.print("You cannot afford to do that!")
                        else:
                            gui.print("That is not the location of one of your settlements!")
                    except Exception as e:
                        print("Something failed!")
                        print(e)
                if arg in ("d", "devcard"):
                    cost = PRICES["devcard"]
                    if game_state.pays(n, cost):
                        game_state.dir_devcards[n] += 1
                        gui.print(f"Player {n} bought a devcard.")
                    elif not DEBUG:
                        gui.print("You cannot afford to do that!")

            # Command play devcard
            elif command in ("p", "play", "d", "devcard"):
                if game_state.dir_devcards[n] > 0:
                    game_state.update_armies(n)
                    hexcoor, player2 = players[n].set_robber(game_state)
                    game_state.robber = hexcoor
                    if not player2 == None:
                        resource = game_state.choose_resource_card(player2)
                        if not resource == None:
                            game_state.dir_resources[player2][resource] -= 1
                            game_state.dir_resources[n][resource] += 1
                    gui.draw_board(game_state)
                    gui.print(f"Player {n} played a knight and robbed player {player2}.")
                    if game_state.largest_army[1] == n:
                        gui.print(f"Player {n} has the larges army!")
                elif not DEBUG:
                    gui.print(f"You do not have a devcard.")
            else:
                gui.print(f"Unknown action: {action}")

        if turn%(10*number_players) == 0:
            gui.draw_board(game_state)
            #game_state.print_state()
            #if input("Pause...") in ("q", "quit"):
                #running = False
        n = (n+1)%number_players

    gui.draw_board(game_state)

    vps = {}
    for n in range(number_players):
        vps[n] = game_state.victory_points(n)
    gui.print("The game ends!")
    for n in range(number_players):
        print(f"Player {n} has {vps[n]} victory points!")
    print(f"The winner is player {winner}!")

#def test(self):
#    n = roll_dice()
#    settlements = [[1,1],[-1,-1]]
#    yields = []
#    #print(HEXCOORS)
#    print("The dice rolled a {0}.".format(n))
#    for settlement in settlements:
#        for vic in VICINITIES:
#            h = vec_add(settlement,vic)
#            #print(h)
#            if h in self.dir_chips.keys():
#                #print(h,self.dir_chips[h], n)
#                if self.dir_chips[h] == n:
#                    yields.append(self.dir_hexes[h])
#    #print(n, yields)
#    print("The settlements {0} earned {1}.".format(settlements,yields))

##################
#   AI CLASSES   #
##################


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
                    points += dir_points[game_state.dir_chips[hexcoor]]
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
        while True:
            #raw_crossing = input("Where do you want to build your settlement? (Two numbers separated by space) ")
            raw_crossing = input("\nWhere do you want to build your settlement? ")
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

########################
#   TURTLE GUI CLASS   #
########################


class GuiMinimal:
    def ask_number_players(self):
        while True:
            n = input("How many players will play? ")
            if n in ("3", "4"):
                return int(n)
            else:
                print("Invalid answer, only 3 or 4 players possible!")

    def ask_player_type(self, number, list_type):
        print("TEST")
        print(COMONLY)
        if (number == 0) and (not COMONLY):
            print("hey")
            return AIUser
        else:
            return AICom
    
    def draw_board(self, game_state):
        game_state.print_state()

    def intro(self):
        s = "WELCOME TO HESPERUS"
        t = "*****"
        s = " ".join([t,s,t])
        u = len(s)*"*"
        s = "\n".join([u,s,u])
        print(s)

    def print(self, string):
        print(string)
        #pass

class GuiTurtle(GuiMinimal):
    def __init__(self):
        self.t = Turtle()
        self.s = self.t.getscreen()
        self.s.tracer(False)
        self.s.mode("logo")
        self.clear()

    def clear(self):
        self.s.clear()
        self.s.mode("logo")
        self.s.tracer(False)

    def draw_board(self, game_state):
        self.clear()
        self.t.pu()
        self.t.goto(hex2cart(( 3,-3)))
        self.t.fillcolor(COLORS["sea"])
        self.t.begin_fill()
        self.t.goto(hex2cart(( 6, 3)))
        self.t.goto(hex2cart(( 3, 6)))
        self.t.goto(hex2cart((-3, 3)))
        self.t.goto(hex2cart((-6,-3)))
        self.t.goto(hex2cart((-3,-6)))
        self.t.goto(hex2cart(( 3,-3)))
        self.t.end_fill()

        # Draw hexes
        for coor, h in game_state.dir_hexes.items():
            color = COLORS[h]
            self.t.goto(hex2cart(coor))
            self.t.pu()
            self.drawhex(color)

        # Draw chips
        self.t.pencolor((0,0,0))
        for coor, chip in game_state.dir_chips.items():
            self.t.goto(hex2cart(coor))
            self.t.write(str(chip), align="center", font=("Sans", 14, "normal"))

        # Draw roads
        self.t.pensize(6)
        for path, piece in game_state.dir_paths.items():
            if piece == None:
                continue
            else:
                coors = list(path)
                color = COLORS["player"+str(piece)]
                self.t.pencolor(color)
                self.t.goto(hex2cart(coors[0]))
                self.t.pd()
                self.t.goto(hex2cart(coors[1]))
                self.t.pu()

        # Draw settlements and cities
        for coor, piece in game_state.dir_crossings.items():
            if piece == None:
                continue
            else:
                if piece[0] == 1:
                    color = COLORS["player"+str(piece[1])]
                    self.t.goto(hex2cart(coor))
                    self.t.dot(20, color)
                elif piece[0] == 2:
                    color = COLORS["player"+str(piece[1])]
                    self.t.goto(hex2cart(coor))
                    self.t.dot(35, color)

        # Draw robber
        self.t.goto(hex2cart(game_state.robber))
        self.t.dot(35, COLORS["robber"])

    def drawhex(self, color):
        t = self.t
        p,h = t.pos(),t.heading()
        t.seth(0)
        t.pu()
        t.fd(HEX_LENGTH)
        t.rt(120)
        t.pensize(2)
        t.pencolor(COLORS["road"])
        t.pd()
        t.fillcolor(color)
        t.begin_fill()
        for i in range(6):
            t.fd(HEX_LENGTH)
            t.rt(60)
        t.end_fill()
        t.pu()
        t.goto(p)
        t.seth(h)

    ### INTRO ANIMATION
    def intro(self):
        t = self.t
        t.ht()
        t.pu()
        s = self.s

        # Sky circle
        t.goto(RADIUS, 0)
        t.seth(180)
        if not DEBUG:
            s.tracer(True)
        t.pencolor(COLORS["sky"])
        t.pensize(4)
        t.pd()
        t.fillcolor(COLORS["sky"])
        t.begin_fill()
        t.circle(-RADIUS)
        t.end_fill()
        t.pu()
        if not DEBUG:
            s.tracer(False)

        # Star
        t.goto(0, 1/2*RADIUS)
        t.seth(0)
        t.pencolor(COLORS["star"])
        t.pensize(2)
        t.pd()
        t.fd(STAR)
        t.fillcolor(COLORS["star"])
        t.begin_fill()
        for i in range(4):
            t.lt(180)
            t.circle(-STAR,90)
        t.end_fill()
        t.goto(0,1/2*RADIUS)
        t.seth(0)
        for i in range(4):
            t.lt(30)
            t.fd(STAR)
            t.bk(STAR)
            t.lt(30)
            t.fd(STAR)
            t.bk(STAR)
            t.lt(30)
        t.pu()

        # Silhouette
        t.goto(RADIUS, 0)
        t.seth(180)
        t.fillcolor(COLORS["ground"])
        t.begin_fill()
        t.circle(-RADIUS,180)
        t.rt(90)
        t.fd(RADIUS-7/4*HOUSE)
        t.lt(90)
        t.fd(HOUSE)
        t.rt(30)
        t.fd(HOUSE)
        t.rt(120)
        t.fd(HOUSE)
        t.rt(30)
        t.fd(HOUSE)
        t.lt(90)
        t.fd(1/2*HOUSE)
        t.lt(90)
        t.fd(3/2*HOUSE)
        t.rt(30)
        t.fd(HOUSE)
        t.rt(120)
        t.fd(HOUSE)
        t.rt(30)
        t.fd(1/2*HOUSE)
        t.lt(90)
        t.fd(HOUSE)
        t.rt(90)
        t.fd(HOUSE)
        t.lt(90)
        t.fd(RADIUS-7/4*HOUSE)
        t.end_fill()

        # Title
        s.update()
        t.goto(0,-1/2*RADIUS)
        if not DEBUG:
            print("Now sleeping, you are not in debug mode!")
            time.sleep(1)
        t.write("Hesperus", align="center", font=("Serif", 50, "bold"))
        s.update()
        if not DEBUG:
            time.sleep(3)
        time.sleep(0.3)
        t.reset()


#####################
#   MAIN FUNCTION   #
#####################


def test():
    n = 100
    list_time = []
    for i in range(n):
        start = time.time()
        run(gui)
        list_time.append(time.time()-start)
    mu = sum(list_time)/n
    sigma = np.sqrt( sum([(t-mu)**2 for t in list_time]) /n)
    print(mu, sigma)

def main():
    global DEBUG
    if input("Start in debug mode? ") in ("n", "N", "no"):
        DEBUG = False
    else:
        DEBUG = True
    if input("Let the computer play against itself? ") in ("n", "N", "no"):
        COMONLY = False
    else:
        COMONLY = True

    gui = GuiTurtle()
    #gui = GuiMinimal()
    gui.intro()
    if COMONLY:
        test()
    else:
        run(gui)
    input("Hesperus terminated successfully! (Press enter to exit)")

if __name__=="__main__":
    main()
