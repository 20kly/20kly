# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# A model for the movement of steam within the system.

FRAME_RATE = 30         # frames per second

SOURCE_LOSS = 1000000
BASE_WELL_PRODUCTION = 150

CONDUCTANCE = { 1 : 100 }
PIPE_CURRENT_LIMIT = { 1 : 100 }



PERSON_STEAM = 1            # amount of steam required per person per frame
WORK_UNIT_STEAM = 5000      # amount of steam required for a work unit

CONSERVATISM = 1000         # life support reserve size, per person per frame

from colours import *

SUB_PIPES = [ 
    (10, 15, DARK_GREEN), # 15% of throughput at resist factor 10 - low
    (12, 40, YELLOW_GREEN), # 40% of throughput at resist factor 12 - normal
    (20, 25, ORANGE_GREEN), # 25% of throughput at resist factor 20 - high
    (90, 20, DARK_ORANGE), # remaining 20% at resist factor 90     - overload
]
