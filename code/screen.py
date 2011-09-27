# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


import pygame
from pygame.locals import *

import config

MODE_FLAGS = RESIZABLE

clock = None
surface = None
__update_size = None

def Get_Event(blocking):
    if blocking:
        e = pygame.event.wait()
    else:
        e = pygame.event.poll()

    if e.type == VIDEORESIZE:
        global __update_size
        __update_size = e.size

    return e

def Initialise():
    global clock, surface, __update_size

    __update_size = config.cfg.resolution
    Update_Resolution()
    clock = pygame.time.Clock()

def Update_Resolution():
    global __update_size, surface

    if __update_size != None:
        (width, height) = __update_size
        width = max(width, 800)
        height = max(height, 550)
        size = (width, height)

        if ((surface == None)
        or (config.cfg.resolution != size)
        or (__update_size != size)):

            config.cfg.resolution = size
            surface = pygame.display.set_mode(size, MODE_FLAGS)
            __update_size = None

    return config.cfg.resolution


