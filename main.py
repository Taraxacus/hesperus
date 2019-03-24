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
from game import run
from test import test


def main():
    # Ask variables
    global DEBUG
    global COMONLY
    if input("Start in debug mode? ") in ("n", "N", "no"):
        DEBUG = False
    else:
        DEBUG = True
    if input("Let the computer play against itself? ") in ("n", "N", "no"):
        COMONLY = False
    else:
        COMONLY = True
    if COMONLY:
        if input("Run some test games? ") in ("n", "N", "no"):
            tests = False
        else:
            tests = True
    else:
        tests = False

    # Set gui
    if tests:
        gui = GuiMinimal(test=True)
    else:
        gui = GuiTurtle()

    # Run gui intro
    gui.intro()

    # Run tests/game
    if tests:
        test(gui)
    else:
        run(gui)

    # Exit
    input("Hesperus terminated successfully! (Press enter to exit)")

if __name__=="__main__":
    main()
