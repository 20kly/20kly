# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

import os, pickle
import config

COSFP = 24
SQRTFP = 4
cos_table = None

def Angle(angle, radius, (cx, cy) = (0, 0)):
    """Return cosine/sine pair for the given angle (degrees)
    scaled for the given radius."""
    angle %= 360
    if angle < 0:
        angle += 360

    x = cx + ((cos_table[ angle ] * radius) >> COSFP)
    y = cy + ((cos_table[ (angle + 90) % 360 ] * radius) >> COSFP)

    return (x, y)

def Distance(x, y):
    return Int_Sqrt((x * x) + (y * y))
   
def Int_Sqrt(a):
    assert a >= 0
    x1 = 0
    x2 = a = a << (SQRTFP * 2)
    while abs(x1 - x2) > 1:
        x1 = x2
        x2 = (x1 + (a / x1)) / 2

    return x2 >> SQRTFP

# Why is a cosine table stored on disk, when cosines can be computed
# essentially trivially? Answer - avoiding floating-point calculations
# in the program.
# Why avoid floating point calculations? Answer - portability. You may
# get different behaviour on different CPUs and architectures. 
# Why is portability important? Answer - demos, save games, network
# games, reproducibility of test scripts and scores. Only possible
# if we can be sure that the cosine table is always the same!

def Initialise():
    global cos_table
    cos_table = pickle.load(file(
                    os.path.join(config.DATA_DIR, "cos.dat"), "rb"))
    assert len(cos_table) == 360
    assert type(cos_table) == list
    assert type(cos_table[ 0 ]) == int
    assert cos_table[ 0 ] == (1 << COSFP)

