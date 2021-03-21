#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import main, mail
from .primitives import *
from .game_types import *
from .unit_test import *


def test_Review_Stats() -> None:
    """Test for review.py.

    Testing is done by code coverage here."""

    # start a game and win it
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_p), # peaceful
                  NoEvent()]

    # step through some game time
    for i in range(10):
        event_list.append(NoEvent())

    # use a cheat
    event_list += [Push(pygame.K_F8), # lose the game
                   NoEvent(),
                   NoEvent(),
                   NoEvent(),
                   NoEvent(),
                   Push(pygame.K_ESCAPE),  # can't return to the game
                   NoEvent(),
                   Push(pygame.K_s),  # can't save
                   NoEvent(),
                   Push(pygame.K_r),  # review stats
                   NoEvent()]

    # step through all graphs
    for i in range(8):
        event_list.append(Push(pygame.K_RIGHT))
        event_list.append(NoEvent())

    event_list += [Push(pygame.K_LEFT),
                   NoEvent(),
                   VideoResize(),
                   NoEvent(),
                   Other(),
                   NoEvent(),
                   Push(pygame.K_ESCAPE),
                   NoEvent(),
                   Quit(),
                   NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))
    assert "GAME END CHEAT (LOSE)" in mail.Get_Messages()
    assert "The City ran out of steam" in mail.Get_Messages()

