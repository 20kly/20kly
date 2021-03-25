#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from lib20k import main
from lib20k.primitives import *
from lib20k.game_types import *
from .unit_test import *

def test_Game_4K() -> None:
    """See the main menu, game screen and game menu at a high resolution."""
    event_list = [NoEvent(),
                  Screenshot("main4k.png"),
                  NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_i), # intermediate
                  NoEvent(),
                  Screenshot("game4k.png"),
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Screenshot("menu4k.png"),
                  NoEvent(),
                  Push(pygame.K_s),         # save
                  NoEvent(),
                  Screenshot("save4k.png"),
                  NoEvent(),
                  Push(pygame.K_1),         # slot 1
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_r),         # restore
                  NoEvent(),
                  Screenshot("restore4k.png"),
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # cancel
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_F10),       # exit game
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=["--test-height=4000"],
              event=Fake_Events(event_list))
    config.cfg.Reset()
    config.Save()
