# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


from pygame.locals import *

# Developers's controls:
DEBUG = False # enables cheats
DEBUG_UPDATES = False
DEBUG_GRID = False

FPS = 16
FPX = 1 << FPS

# Arbitrary constants
BUILD_NODE = 1
BUILD_PIPE = 2
DESTROY = 3
UPGRADE = 4
NEUTRAL = 5
OPEN_MENU = 6

SEASON_QUIET = 104
SEASON_STORM = 105
SEASON_ALIEN = 106
SEASON_QUAKE = 107
SEASON_START = 108

MENU_SAVE = 201
MENU_LOAD = 202
MENU_HIDE = 203
MENU_QUIT = 204
MENU_FULLSCREEN = 205
MENU_TUTORIAL = 206
MENU_NEW_GAME = 207
MENU_RES = 208
MENU_MENU = 209
MENU_REVIEW = 210
MENU_BEGINNER = 211
MENU_INTERMEDIATE = 212
MENU_EXPERT = 213
MENU_PREV = 214
MENU_NEXT = 215
MENU_UPDATES = 216
MENU_WEBSITE = 217
MENU_RESIZE_EVENT = 218
MENU_LOOP_RUN = 219
MENU_CONTINUE = 220
MENU_MUTE = 221
MENU_MANUAL = 222



# work and upgrades:
NODE_MAX_TECH_LEVEL = 5
NODE_UPGRADE_WORK = 10
CITY_UPGRADE_WORK = 15
PIPE_MAX_TECH_LEVEL = 3
PIPE_UPGRADE_WORK_FACTOR = 10

# timing:
LENGTH_OF_SEASON = 120 # seconds (game days)

# the grid:
GRID_CENTRE = (25,25)
GRID_SIZE = (50,50)

# misc:
CITY_BOX_SIZE = 10
CGISCRIPT = "http://www.jwhitham.org/cgi-bin/LYU.cgi?"

# version 2.0
MAX_PIPE_LENGTH = 20 # tgrid
LARGE_NUMBER = 1 << 30
WORK_VELOCITY = 5 * FPX

# non-scaled sizes
SCROLL_MARGIN = 15
POPUP_SIZE = 48
POPUP_RADIUS = 150

# things that are set by the difficulty mode:
class Difficulty:
    def __init__(self):
        self.Set(MENU_INTERMEDIATE)
    
    def Set(self, level):
        pass


DIFFICULTY = Difficulty()

def Scr_To_Grid((x,y)):
    return (x / __grid_size, y / __grid_size)

def Grid_To_Scr((x,y)):
    return (( x * __grid_size ) + __h_grid_size,
            ( y * __grid_size ) + __h_grid_size )

def Grid_To_Scr_Rect((x,y)):
    (cx,cy) = Grid_To_Scr((x,y))
    return Rect(cx - __h_grid_size_1, cy - __h_grid_size_1, 
            __grid_size_1, __grid_size_1)

def Set_Grid_Size(sz):
    global __grid_size, __grid_size_1, __h_grid_size, __h_grid_size_1
    __grid_size = sz
    __grid_size_1 = sz - 1
    __h_grid_size = sz / 2
    __h_grid_size_1 = __h_grid_size - 1

def Get_Grid_Size():
    return __grid_size

Set_Grid_Size(10)


