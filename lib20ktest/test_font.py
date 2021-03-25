#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame
from lib20k import font
from lib20k.game_types import *
from lib20k.primitives import *
from . import unit_test



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

