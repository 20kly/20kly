# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

import pygame
from pygame.locals import *

import resource

__font_objects = dict()
__font_scale = 0


def Get_Font(size):
    size += __font_scale
    if ( size < 6 ): 
        size = 6

    return __Get_Font(size)

def __Get_Font(size):
    if ( not __font_objects.has_key(size) ):
        __font_objects[ size ] = resource.Load_Font(size)
    return __font_objects[ size ]

def Scale_Font(height):
    # Previously - font scale 4 at 1024, 768
    # meant that sizes were 1-1 on the screen at that res.
    # Say this means 25 lines on screen for 18 point text.
    reference_size = 18
    reference_height = height / 25

    # Find the font size producing this height
    too_much = 200
    too_little = 6
    run = True
    while run and (too_much > (too_little + 1)):
        actual_size = (too_much + too_little) / 2
        actual_height = __Get_Font(actual_size).get_height()

        if actual_height > reference_height:
            too_much = actual_size
        elif actual_height < reference_height:
            too_little = actual_size
        else:
            run = False
    
    global __font_scale
    __font_scale = actual_size - 18





