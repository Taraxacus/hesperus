#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# ui.py:

from turtle import Turtle
import time
import numpy as np

from constants import *
#from gamestate import GameState
#from ai import AICom

COORDINATE_MATRIX1 = np.matrix([[0, 1], [np.cos(np.pi/6), -1/2]])
COORDINATE_MATRIX2 = np.linalg.inv(COORDINATE_MATRIX1)

RADIUS = 300 # Radius of logo in intro
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
          "X":(0.7, 0.2,   1),
         }

HEX_LENGTH = 60

def cart2hex(v):
    return 1/HEX_LENGTH * (np.matrix(v) * COORDINATE_MATRIX2)

def hex2cart(u):
    r = (HEX_LENGTH * (u*COORDINATE_MATRIX1)).tolist()
    # r is now a list containing exactly one list.
    r = tuple(r[0])
    return r

class UiMinimal:
    def __init__(self,test=False):
        self.test = test

    def ask_number_players(self):
        while True:
            n = input("How many players will play? ")
            if n in ("3", "4"):
                return int(n)
            else:
                print("Invalid answer, only 3 or 4 players possible!")

    def ask_player_type(self, number, dict_ai):
        #print("TEST")
        #print(COMONLY)
        #if (number in (0,1)) and (not COMONLY):
            #print("hey")
            #return AIUser
        #else:
            #return AICom
        #if COMONLY:
            #return AICom
        #else:
        while True:
            player_types = dict_ai.keys()
            s = ", ".join(player_types)
            raw_player = input(f"Who shall play player {number}? ("+s+") ").lower()
            if raw_player in dict_ai.keys():
                return dict_ai[raw_player]
            print("That is not a valid player type!")

    def ask_players(self, dict_ai):
        number_players = self.ask_number_players()
        players = []
        for n in range(number_players):
            AIClass = self.ask_player_type(n, dict_ai)
            players.append(AIClass(n))
        # Do list comprehension?
        return players
    
    def draw_board(self, game_state):
        if not self.test:
            game_state.print_state()

    def intro(self):
        s = "WELCOME TO HESPERUS"
        t = "*****"
        s = " ".join([t,s,t])
        u = len(s)*"*"
        s = "\n".join([u,s,u])
        print(s)

    def print(self, string):
        if not self.test:
            print(string)
        #pass

class GuiTurtle(UiMinimal):
    def __init__(self, test=False):
        self.test = test

        self.t = Turtle()
        self.s = self.t.getscreen()
        self.s.mode("logo")
        self.clear()

    def clear(self):
        self.s.reset()
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

        # Draw ports
        for port in game_state.dir_ports:
            for coor in port:
                color = COLORS[game_state.dir_ports[port]]
                self.t.goto(hex2cart(coor))
                self.t.dot(40, color)

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
                    self.t.dot(30, color)

        # Draw robber
        self.t.goto(hex2cart(game_state.robber))
        self.t.dot(35, COLORS["robber"])

        # Sleep for a moment
        self.s.update()
        time.sleep(0.1)

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
        if DEBUG: # and __name__ == "__main__":
            return
        t = self.t
        t.ht()
        t.pu()
        s = self.s
        s.update()

        # Sky circle
        t.goto(RADIUS, 0)
        t.seth(180)
        #s.tracer(True)
        t.pencolor(COLORS["sky"])
        t.pensize(4)
        t.pd()
        t.fillcolor(COLORS["sky"])
        t.begin_fill()
        #t.circle(-RADIUS)
        for i in range(12):
            time.sleep(0.1)
            t.circle(-RADIUS, 30)
            s.update()
            #print("30deg")
        t.end_fill()
        t.pu()
        #s.tracer(False)
        s.update()

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
        s.update()

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
        s.update()

        # Title
        #s.update()
        t.goto(0,-1/2*RADIUS)
        #s.update()
        print("Now sleeping, you are not in debug mode!")
        time.sleep(1)
        t.write("Hesperus", align="center", font=("Serif", 50, "bold"))
        #s.update()
        time.sleep(3)
        time.sleep(0.3)
        t.reset()

def main():
    UiMinimal()
    GuiTurtle()

if __name__ == "__main__":
    main()
