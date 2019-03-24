#!/usr/bin/python
# Author: Maximilian Weinberg
# Date: 2019-03-24
# constants.py: Some constants used for hesperus

import numpy as np

COORDINATE_MATRIX1 = np.matrix([[0, 1], [np.cos(np.pi/6), -1/2]])
COORDINATE_MATRIX2 = np.linalg.inv(COORDINATE_MATRIX1)

DEBUG = True
COMONLY = True

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

