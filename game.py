#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# game.py:

import time

from constants import *
from gamestate import GameState
from ai import *

def roll_dice():
    return randint(1,6)+randint(1,6)

def run(gui):
    times = []
    time_start = time.time()

    # Initialize players
    if not COMONLY:
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

    times.append(time.time() - time_start)
    # Initial settlements
    gui.print("\n" + 5*"*" + " INITIAL SETTLEMENTS " + 5*"*" + "\n")
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

    times.append(time.time() - time_start)
    # Actual game loops
    gui.print("\n" + 5*"*" + " GAME STARTS " + 5*"*" + "\n")
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

        #gui.print("\n" + 5*"*" + f" ROUND {roundd}, TURN {turn}, PLAYER {n} " + 5*"*" + "\n")
        gui.print("\n" + 5*"*" + f" TURN {turn}, PLAYER {n} " + 5*"*" + "\n")

        # Dice roll
        w = roll_dice()
        gui.print(f"Player {n} rolled a {w}.")

        if w == 7:
            # Robber
            for m in range(number_players):
                hand = game_state.number_resources(m)
                if hand > 7:
                    players[m].get_robbed(game_state)
                    if not game_state.number_resources(m) == (hand - hand//2):
                        gui.print("Player {m} cheated the robber!")
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
            gui.draw_board(game_state)

        if turn%(10*number_players) == 0:
            gui.draw_board(game_state)
            #game_state.print_state()
            #if input("Pause...") in ("q", "quit"):
                #running = False
        n = (n+1)%number_players
        #print(n)

    vps = {}
    for n in range(number_players):
        vps[n] = game_state.victory_points(n)
    gui.print("The game ends!")
    for n in range(number_players):
        gui.print(f"Player {n} has {vps[n]} victory points!")
    gui.print(f"The winner is player {winner}!")

    times.append(time.time() - time_start)
    return turn, times

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