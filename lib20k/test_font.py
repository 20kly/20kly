#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame
from . import font, unit_test
from .game_types import *
from .primitives import *



def test_font() -> None:
    test_surface = unit_test.Setup_For_Unit_Test()
    colour = (255, 255, 255)

    y = 0
    for size in range(10, 51):
        f = font.Get_Font_Pixel_Size(size)
        s = f.render("EXAMPLE TEXT qwerty |][!", True, colour)
        r = s.get_rect()
        test_surface.blit(s, (0, y))
        y += r.height

        assert abs(r.height - size) <= 1
        pygame.display.flip()

