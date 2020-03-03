#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-10
# aedificator.py:

from constants import *
from player import AI
#import tensorflow as tf

# For testing
from gamestate import GameState
from ui import GuiMinimal

res2num = {"L":-1, "B":-2, "G":-3, "W":-4, "O":-5, "D":-6}

def gamestate2dic(gamestate):
    # Board
    dic1 = {}
    dic2 = {}
    for i in range(-5,6):
        for j in range(-5, 6):
            pos = (i,j)
            if pos in HEXCOORS:
                dic1[pos] = res2num[gamestate.dir_hexes[pos]]
                if pos in gamestate.dir_chips.keys():
                    dic2[pos] = -gamestate.dir_chips[pos]
                else:
                    dic2[pos] = -1
            elif pos in CROSSINGS:
                if gamestate.dir_crossings[pos] != None:
                    dic1[pos] = gamestate.dir_crossings[pos][0]
                    dic2[pos] = gamestate.dir_crossings[pos][1]
                else:
                    dic1[pos] = 0
                    dic2[pos] = 0
            else:
                dic1[pos] = 0
                dic2[pos] = 0

    # Roads
    dic3 = {}
    for i in range(-5,6):
        for j in range(-5, 6):
            pos1 = (i,j)
            pos2 = (i+1,j)
            pos3 = (i,j-1)
            sets = [{pos1, pos2}, {pos1, pos3}, {pos2, pos3}]
            paths = [frozenset(s) for s in sets]

            dic3[pos1] = 0
            for path in paths:
                if path in PATHS:
                    if gamestate.dir_paths[path] != None:
                        dic3[pos1] = gamestate.dir_paths[path]
                    break

    # Ressources
    dic4 = {}
    for n in range(gamestate.number_players):
        for resource in RESOURCES:
            i = res2num[resource]
            dic4[(n,i)] = gamestate.dir_resources[n][resource]

    # Devcards and knights
    dic5 = gamestate.dir_devcards
    dic6 = gamestate.dir_knights

    return dic1, dic2, dic3, dic4, dic5, dic6

def gamestate2vec(gamestate):
    # Board
    l = []
    l1 = []
    l2 = []
    for i in range(-5,6):
        for j in range(-5, 6):
            pos = (i,j)
            if pos in HEXCOORS:
                l1.append(res2num[gamestate.dir_hexes[pos]])
                if pos in gamestate.dir_chips.keys():
                    l2.append(-gamestate.dir_chips[pos])
                else:
                    l2.append(-1)
            elif pos in CROSSINGS:
                if gamestate.dir_crossings[pos] != None:
                    l1.append(gamestate.dir_crossings[pos][0])
                    l2.append(gamestate.dir_crossings[pos][1])
                else:
                    l1.append(0)
                    l2.append(0)
            else:
                l1.append(0)
                l2.append(0)
    l += l1
    l += l2

    # Roads
    for i in range(-5,6):
        for j in range(-5, 6):
            pos1 = (i,j)
            pos2 = (i+1,j)
            pos3 = (i,j-1)
            sets = [{pos1, pos2}, {pos1, pos3}, {pos2, pos3}]
            paths = [frozenset(s) for s in sets]

            for path in paths:
                if path in PATHS:
                    if gamestate.dir_paths[path] != None:
                        l.append(gamestate.dir_paths[path])
                    else:
                        l.append(0)
                    break

    # Ressources
    for n in range(gamestate.number_players):
        for resource in RESOURCES:
            l.append(gamestate.dir_resources[n][resource])

    # Devcards and knights
    #dic5 = gamestate.dir_devcards
    #dic6 = gamestate.dir_knights
    for n in range(gamestate.number_players):
        l.append(gamestate.dir_devcards[n])
    for n in range(gamestate.number_players):
        l.append(gamestate.dir_knights[n])

    return l

class GuiNN(GuiMinimal):
    def draw_board(self, gamestate):
        dic1, dic2, dic3, dic4, dic5, dic6 = gamestate2dic(gamestate)

        for i in range(-5,6):
            for j in range(-5, 6):
                pos = (i,j)
                s = (4*" " + str(dic1[pos]))[-4:]
                print(s, end="")
            print("")
        print("")

        for i in range(-5,6):
            for j in range(-5, 6):
                pos = (i,j)
                s = (4*" " + str(dic2[pos]))[-4:]
                print(s, end="")
            print("")
        print("")

        for i in range(-5,6):
            for j in range(-5, 6):
                pos = (i,j)
                s = (4*" " + str(dic3[pos]))[-4:]
                print(s, end="")
            print("")
        print("")

        for i in range(gamestate.number_players):
            for j in range(-5,0):
                pos = (i,j)
                s = (4*" " + str(dic4[pos]))[-4:]
                print(s, end="")
            print("")
        print("")

        for i in range(gamestate.number_players):
            s = (4*" " + str(dic5[i]))[-4:]
            print(s, end="")
        print("")

        for i in range(gamestate.number_players):
            s = (4*" " + str(dic6[i]))[-4:]
            print(s, end="")
        print("")

class Aedificator(AI):
    pass

def main():
    gamestate = GameState(4)
    l = gamestate2vec(gamestate)
    print(l)
    print(len(l))

if __name__=="__main__":
    main()
