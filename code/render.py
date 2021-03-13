#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

import pygame


from . import font
from .game_types import *

# A font renderer that supports the familiar & marker for a hotkey.

def Render(text: str, size: int, colour: Colour, hcolour: Colour) -> SurfaceType:

    i = text.find('&')
    if ( i < 0 ):
        # not found, do normal render
        return font.Get_Font(size).render(text, True, colour)

    f = font.Get_Font(size)
    # do normal render up to &.
    s1 = f.render(text[ : i ], True, colour)

    i += 1
    s2 = f.render(text[ i ], True, hcolour)

    i += 1
    s3 = f.render(text[ i : ], True, colour)

    total_width = sum([ s.get_rect().width for s in [ s1, s2, s3 ] ])
    s = pygame.Surface((total_width, s3.get_rect().height))
    s.set_colorkey((0,0,0))

    x = 0
    s.blit(s1,(x,0))
    x += s1.get_rect().width
    s.blit(s2,(x,0))
    x += s2.get_rect().width
    s.blit(s3,(x,0))
    return s

