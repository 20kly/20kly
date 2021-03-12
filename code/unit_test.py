#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import os, pygame, pickle
from . import game_random, game, save_game, resource, config, startup, extra
from . import events, menu, main, mail, map_items, network, grid, quiet_season
from .ui import User_Interface
from .primitives import *
from .game_types import *


def Setup_For_Unit_Test() -> SurfaceType:
    resource.DATA_DIR = os.path.join(os.getcwd(), "data")
    resource.No_Sound()
    pygame.init()
    pygame.font.init()
    return pygame.display.set_mode((MINIMUM_WIDTH, MINIMUM_HEIGHT), pygame.RESIZABLE)

class Click(events.Event):
    def __init__(self, pos: SurfacePosition) -> None:
        events.Event.__init__(self, pos=pos,
                              t=pygame.MOUSEBUTTONDOWN, button=1)

class RightClick(events.Event):
    def __init__(self, pos: SurfacePosition) -> None:
        events.Event.__init__(self, pos=pos,
                              t=pygame.MOUSEBUTTONDOWN, button=2)

class Move(events.Event):
    def __init__(self, pos: SurfacePosition) -> None:
        events.Event.__init__(self, pos=pos, t=pygame.MOUSEMOTION)

class Push(events.Event):
    def __init__(self, key: int) -> None:
        events.Event.__init__(self, key=key, t=pygame.KEYDOWN)

class Other(events.Event):
    def __init__(self) -> None:
        events.Event.__init__(self, t=pygame.KEYUP)

class Quit(events.Event):
    def __init__(self) -> None:
        events.Event.__init__(self, t=pygame.QUIT)

class VideoResize(events.Event):
    def __init__(self) -> None:
        events.Event.__init__(self, t=pygame.VIDEORESIZE)

class NoEvent(events.Event):
    pass

class Fake_Events(events.Events):
    def __init__(self, event_list: List[events.Event]) -> None:
        events.Events.__init__(self)
        self.event_list = event_list
        self.index = 0
        self.is_testing = True

    def real_poll(self) -> None:
        e = pygame.event.poll()
        while e.type != pygame.NOEVENT:
            e = pygame.event.poll()

    def wait(self) -> events.Event:
        self.real_poll()
        return self.poll()

    def poll(self) -> events.Event:
        self.real_poll()
        assert self.index < len(self.event_list)
        self.index += 1
        return self.event_list[self.index - 1]

    def webbrowser_open(self, url: str) -> None:
        mail.New_Mail("OPEN URL " + url)

    def check_update(self, url: str) -> str:
        mail.New_Mail("CHECK UPDATE URL " + url)
        return "9.9"
