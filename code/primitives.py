#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


import math
import enum

# Developers's controls:
DEBUG = False # enables cheats
DEBUG_UPDATES = False
DEBUG_GRID = False


# Arbitrary constants
class Season(enum.Enum):
    QUIET = 104
    STORM = 105
    ALIEN = 106
    QUAKE = 107
    START = 108

class MenuCommand(enum.Enum):
    BUILD_NODE = 1
    BUILD_PIPE = 2
    DESTROY = 3
    UPGRADE = 4
    NEUTRAL = 5
    OPEN_MENU = 6
    SAVE = 201
    LOAD = 202
    HIDE = 203
    QUIT = 204
    FULLSCREEN = 205
    TUTORIAL = 206
    NEW_GAME = 207
    MENU = 209
    REVIEW = 210
    BEGINNER = 211
    INTERMEDIATE = 212
    EXPERT = 213
    PREV = 214
    NEXT = 215
    UPDATES = 216
    WEBSITE = 217
    MANUAL = 218
    MUTE = 219
    PEACEFUL = 220
    SAVE0 = 400
    SAVE1 = 401
    SAVE2 = 402
    SAVE3 = 403
    SAVE4 = 404
    SAVE5 = 405
    SAVE6 = 406
    SAVE7 = 407
    SAVE8 = 408
    SAVE9 = 409
    UNUSED = 410
    CANCEL = 411

# Playback and record
class PlayMode(enum.Enum):
    OFF = 301
    PLAYBACK = 302
    RECORD = 303
    PLAYTHRU = 304

# Mathematical constants
HALF_PI = math.pi * 0.5
TWO_PI = math.pi * 2.0
TWO_THIRDS_PI = ( math.pi * 2.0 ) / 3.0


# Game constants, for tuning:
# steam:
INITIAL_NODE_CAPACITY = 50
CAPACITY_UPGRADE = 15
RESISTANCE_FACTOR = 0.55 # 0.65
WORK_STEAM_DEMAND = 4.52
STATIC_STEAM_DEMAND = 2.85

# work and health:
HEALTH_UNIT = 10
WORK_UNIT_SIZE = 1
NODE_HEALTH_UNITS = 20
STORM_DAMAGE = 1

# work and upgrades:
NODE_MAX_TECH_LEVEL = 5
NODE_UPGRADE_WORK = 10
CITY_UPGRADE_WORK = 15
PIPE_MAX_TECH_LEVEL = 3
PIPE_UPGRADE_WORK_FACTOR = 1.0
PIPE_UPGRADE_RESISTANCE_FACTOR = 0.8

# timing:
LENGTH_OF_SEASON = 120 # seconds (game days)

# pressure:
PRESSURE_DANGER = 4.0
PRESSURE_WARNING = 6.0
PRESSURE_OK = 8.0
PRESSURE_GOOD = 10.0

# the grid:
GRID_CENTRE = (25,25)
GRID_SIZE = (50,50)

# misc:
CITY_BOX_SIZE = 10
CITY_COLOUR = (192,128,0)
RESOLUTION = (1024, 768)
CGISCRIPT = "http://www.jwhitham.org/cgi-bin/LYU.cgi?"

