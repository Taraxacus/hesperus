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

#COORDINATE_MATRIX1 = np.matrix([[1,0], [-1/2, cos(pi/6)]])
COORDINATE_MATRIX1 = np.matrix([[0, 1], [cos(pi/6), -1/2]])
COORDINATE_MATRIX2 = np.linalg.inv(COORDINATE_MATRIX1)
#VICINITIES = [[1,1],[1,0],[0,-1],[-1,-1],[-1,0],[0,1]]
VICINITIES = [(1,0), (1,1), (0,1), (-1,0), (-1,-1), (0,-1)]

DEBUG = False

RADIUS = 300
HOUSE  = 50
STAR   = 30
COLORS = {"sky":(0,0,0.3),
          "ground":(0,0,0),
          "star":(1,1,0.5),
          "road":(0.8,0.5,0.2),

          "pink":(1,0.3,0.7),
          "L":(  0, 0.4,   0),
          "B":(  1, 0.5, 0.4),
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

HEXES = 4*["L"] + 3*["B"] + 4*["G"] + 4*["W"] + 3*["O"] + ["D"]
SPIRALS = [[ 1, 2, 3, 7,12,16,19,18,17,13, 8, 4, 5, 6,11,15,14, 9,10],
           [ 3, 7,12,16,19,18,17,13, 8, 4, 1, 2, 6,11,15,14, 9, 5,10],
          ]
CHIP_ORDERS = [[HEXCOORS[i-1] for i in spiral] for spiral in SPIRALS]
CHIPS = [ 5, 2, 6, 3, 8,10, 9,12,11, 4, 8,10, 9, 4, 5, 6, 3,11]
#CHIPS = list(range(19))
NO_YIELDS = ["D"]
#CHIP_FONT = [2:("Arial", 8, "normal"),

def roll_dice():
    return randint(1,6)+randint(1,6)

def vec_add(v1,v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

###################
#   COORDINATES   #
###################


def cart2hex(v):
    return 1/HEX_LENGTH * (np.matrix(v) * COORDINATE_MATRIX2)

def hex2cart(u):
    r = (HEX_LENGTH * (u*COORDINATE_MATRIX1)).tolist()
    # r is now a list containing exactly one list.
    r = tuple(r[0])
    return r


###############
#   DRAWING   #
###############



##################
#   GAME CLASS   #
##################


class Game:
    def __init__(self, gui):
        self.gui = gui

    def init(self):
        if not DEBUG:
            self.number_players = self.gui.ask_number_players()
        else:
            self.number_players = 3
        for i in range(self.number_players):
            # Ask whether this player is a human or an AI,
            # and more specifically, WHAT AI.
            pass

        # Randomize board
        hexes = HEXES.copy()
        shuffle(hexes)
        self.dir_hexes = dict(zip(HEXCOORS, hexes))
        #print(self.dir_hexes)
        chip_order = choice(CHIP_ORDERS)
        #print(chip_order)
        #self.dir_chips = {chip_order[i]:CHIPS[i] for i in range(len(CHIPS))}
        self.dir_chips = {}
        j = 0
        for coor in chip_order:
            if self.dir_hexes[coor] not in NO_YIELDS:
                self.dir_chips[coor] = CHIPS[j]
                #print(coor, j, CHIPS[j])
                j+=1
        #print(self.dir_chips)
        self.gui.draw_board(self.dir_hexes, self.dir_chips)

    def run(self):
        n = roll_dice()
        settlements = [[1,1],[-1,-1]]
        yields = []
        #print(HEXCOORS)
        print("The dice rolled a {0}.".format(n))
        for settlement in settlements:
            for vic in VICINITIES:
                h = vec_add(settlement,vic)
                #print(h)
                if h in self.dir_chips.keys():
                    #print(h,self.dir_chips[h], n)
                    if self.dir_chips[h] == n:
                        yields.append(self.dir_hexes[h])
        #print(n, yields)
        print("The settlements {0} earned {1}.".format(settlements,yields))
        return False

    def exit(self):
        pass


########################
#   TURTLE GUI CLASS   #
########################


class GuiTurtle:
    def __init__(self):
        self.t = Turtle()
        self.s = self.t.getscreen()
        self.s.clear()
        self.s.mode("logo")
        self.s.tracer(False)

    def ask_number_players(self):
        while True:
            n = input("How many players will play? ")
            if n in ("3", "4"):
                return int(n)
            else:
                print("Invalid answer, only 3 or 4 players possible!")
    
    def draw_board(self, dir_hexes, dir_chips):
        #self.s.clear()
        for coor, h in dir_hexes.items():
            color = COLORS[h]
            self.t.goto(hex2cart(coor))
            self.t.pu()
            self.drawhex(color)

        self.t.pencolor((0,0,0))
        for coor, chip in dir_chips.items():
            self.t.goto(hex2cart(coor))
            self.t.write(str(chip), align="center", font=("Sans", 14, "normal"))

        print("Board drawn!")

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


def main():
    global DEBUG
    if input("Start in debug mode? ") in ("n", "N", "no"):
        DEBUG = False
    else:
        DEBUG = True
    screen = Screen()
    screen.tracer(False)
    screen.mode("logo")
    #print(COORDINATE_MATRIX1)
    #print(COORDINATE_MATRIX2)

    gui = GuiTurtle()
    game = Game(gui)

    print(DEBUG)
    gui.intro()
    game.init()
    running = True
    while running:
        running = game.run()
    game.exit()
    #if DEBUG:
        #input("Hesperus terminated successfully! (Press enter to exit)")
    input("Hesperus terminated successfully! (Press enter to exit)")

if __name__=="__main__":
    main()
