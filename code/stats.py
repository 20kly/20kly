# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 


import pygame
from pygame.locals import *

import resource

__font_objects = dict()
__font_scale = 0


def Draw_Stats_Window(output, stats_tuple_list):
    y = 5
    w = output.get_rect().width 

    global __font_objects

    for (colour, size, text) in stats_tuple_list:
        if ( size == None ):
            # Draw a bar meter instead!
            assert type(text) == tuple
            items = [ text ]
            Draw_Bar_Meter(output, [text], (w / 2, y + 3), ( w * 4 ) / 5, 6)
            y += 8
        else:
            # Draw text, as usual
            txt = Get_Font(size).render(text, True, colour)
            x = ( w - txt.get_rect().width ) / 2
            output.blit(txt, (x,y))
            y += txt.get_rect().height


def Draw_Bar_Meter(output, items, centre_pos, width, item_height):
    r1 = Rect(0, 0, width, ( item_height * len(items) ) + 1)
    r1.center = centre_pos
    pygame.draw.rect(output, (128,128,128), r1)
    y = r1.top + 1
    w = width - 2
    h = item_height - 1

    for (var, var_colour, total, total_colour) in items:
        r2 = Rect(r1.left + 1, y, w, h) # (total)
        pygame.draw.rect(output, total_colour, r2)

        if ( var > 0 ):
            if ( var > total ): var = total
            r3 = Rect(r1.left + 1, y, (( w * var ) / total ), h)
            pygame.draw.rect(output, var_colour, r3)

        y += item_height

    return r1 # bounding box

def Get_Font(size):
    size += __font_scale
    if ( size < 10 ): 
        size = 10

    if ( not __font_objects.has_key(size) ):
        __font_objects[ size ] = resource.Load_Font(size)
    return __font_objects[ size ]

def Set_Font_Scale(fs):
    global __font_scale
    __font_scale = fs - 4




