#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2017-07-01
# main.py: Versuch einer Simulation von Die Siedler von Catan um spaeter
#       eine AI zu implementieren. EXECUTABLE

#import numpy as np
#from constants import *
#from gamestate import GameState
#from ai import *
from ui import *
#from player import dict_ai
from actor import dict_ai
from game import run
from simulation import test

# For testing
#from aedificator import GuiNN

def main():
    # Ask variables
    global DEBUG
    global COMONLY
    #DEBUG = True
    #COMONLY = True

    if input("Start in debug mode? ") in ("n", "N", "no"):
        DEBUG = False
    if input("Let the computer play against itself? ") in ("n", "N", "no"):
        COMONLY = False

    if COMONLY:
        if input("Run some test games? ") in ("n", "N", "no"):
            tests = False
        else:
            tests = True
    else:
        tests = False

    # Set ui
    if tests:
        ui = UiMinimal(test=True)
    else:
        ui = GuiTurtle()
        #ui = GuiNN()

    # Run ui intro
    if not DEBUG:
        ui.intro()

    # Run tests/game
    if tests:
        test(ui)
    else:
        if COMONLY:
            players = [dict_ai["com"](i) for i in range(4)]
        else:
            players = ui.ask_players(dict_ai)
        #number_players = ui.ask_number_players()
        #players = []
        #for n in range(number_players):
            #AIClass = ui.ask_player_type(n, dict_ai)
            #players.append(AIClass(n))

        run(ui, players)

    # Exit
    input("Hesperus terminated successfully! (Press enter to exit)")

if __name__=="__main__":
    main()
