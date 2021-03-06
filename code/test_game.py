#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import main
from .primitives import *
from .game_types import *
from .unit_test import *

def test_Game_Events() -> None:
    """Test for game.py.

    This test looks at the popup menu which can
    appear during the game. Correctness of the test is
    established by 100% coverage of the menu-related code
    within game.py.
    """
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_i), # intermediate
                  NoEvent(),
                  Click((10, 10)),
                  NoEvent(),
                  RightClick((20, 20)),
                  NoEvent(),
                  Move((30, 30)),
                  NoEvent(),
                  Other(),
                  NoEvent(),
                  Click((100, 100)),        # click in unused space
                  NoEvent(),
                  Push(pygame.K_F9),
                  NoEvent(),
                  Push(pygame.K_F10),
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Move((40, 40)),
                  NoEvent(),
                  Click((50, 50)),
                  NoEvent(),
                  RightClick((60, 60)),
                  NoEvent(),
                  Push(pygame.K_m),         # leave menu (clicking mute)
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # leave menu (return to game)
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_r),
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # leave menu (cancelling restore)
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_q),         # leave menu (quit to main menu)
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))

def test_Game_Menu_Quit() -> None:
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_i), # intermediate
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_F10),       # exit game
                  NoEvent(),
                  Push(pygame.K_q),         # leave menu (quit to main menu)
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))

