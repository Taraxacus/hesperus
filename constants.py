#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# constants.py: Some constants used for hesperus

#import numpy as np

DEBUG = True
COMONLY = True

HEXCOORS = [[ 2,-2], [ 3, 0], [ 4, 2],
        [ 0,-3], [ 1,-1], [ 2, 1], [ 3, 3],
    [-2,-4], [-1,-2], [ 0, 0], [ 1, 2], [ 2, 4],
        [-3,-3], [-2,-1], [-1, 1], [ 0, 3],
            [-4,-2], [-3, 0], [-2, 2]]
HEXCOORS = [tuple(i) for i in HEXCOORS]
#HEXCOORS_MAT = [np.matrix(coor) for coor in HEXCOORS]
DIRECTIONS = [[1,0], [1, 1], [0,1], [-1,0], [-1,-1], [0,-1]]
DIRECTIONS = [tuple(i) for i in DIRECTIONS]

NO_YIELDS = ["D"]
#CHIP_FONT = [2:("Arial", 8, "normal"),
RESOURCES = ["L", "B", "G", "W", "O"]

PRICES = {"settlement":{"L":1, "B":1, "G":1, "W":1, "O":0},
        "road":{"L":1, "B":1, "G":0, "W":0, "O":0},
        "city":{"L":0, "B":0, "G":2, "W":0, "O":3},
        "devcard":{"L":0, "B":0, "G":1, "W":1, "O":1}}

def vec_add(v1,v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

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

