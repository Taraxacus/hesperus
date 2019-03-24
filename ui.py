#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# ui.py:

from turtle import Turtle
import time

from constants import *
from gamestate import GameState
from ai import AICom

class GuiMinimal:
    def __init__(self,test=False):
        self.test = test

    def ask_number_players(self):
        while True:
            n = input("How many players will play? ")
            if n in ("3", "4"):
                return int(n)
            else:
                print("Invalid answer, only 3 or 4 players possible!")

    def ask_player_type(self, number, list_type):
        #print("TEST")
        #print(COMONLY)
        #if (number in (0,1)) and (not COMONLY):
            #print("hey")
            #return AIUser
        #else:
            #return AICom
        if COMONLY:
            return AICom
        else:
            while True:
                raw_player = input(f"Who shall play player {number}? ")
                if raw_player.lower() in ("com", "aicom"):
                    return AICom
                elif raw_player.lower() in ("user", "aiuser"):
                    return AIUser
                else:
                    print("That is not a valid player type!")
    
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

class GuiTurtle(GuiMinimal):
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
        if DEBUG and __name__ == "__main__":
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
