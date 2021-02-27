#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import os, pygame
from . import game_random, game, save_game, resource
from .ui import User_Interface
from .primitives import *
from .game_types import *


def Setup_For_Unit_Test() -> SurfaceType:
    resource.DATA_DIR = os.path.join(os.getcwd(), "data")
    resource.No_Sound()
    pygame.init()
    pygame.font.init()
    return pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.RESIZABLE)

def test_game() -> None:
    test_screen = Setup_For_Unit_Test()
    demo = game_random.Game_Random()
    g = game.Game_Data(demo, MenuCommand.INTERMEDIATE)
    ui = User_Interface(g.net, demo, RESOLUTION)
    assert ui.net == g.net
    g.historian_time = 999.0
    result = save_game.Save(g, MenuCommand.SAVE9, "test save")
    assert result is None
    g.historian_time = 123.0

    g2 = game.Restore(ui, g, MenuCommand.SAVE9)
    assert g2 != g
    assert g2.net != g.net                  # network reloaded
    assert ui.net == g2.net                 # ui is updated correctly
    assert g2.historian_time == 999.0       # value restored correctly
    assert g2.net.demo.random() >= -1.0     # check that random numbers can be generated

