#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame, webbrowser, urllib.request
from .game_types import *


class Event:
    def __init__(self, base: Optional[pygame.event.Event] = None,
                 t: int = pygame.NOEVENT,
                 pos: SurfacePosition = (0, 0),
                 key: int = 0,
                 button: int = 0) -> None:

        self.type = t
        self.pos = pos
        self.key = key
        self.button = button

        if base is not None: # NO-COV
            self.type = base.type
            if self.type == pygame.MOUSEMOTION:
                self.pos = base.pos
            elif self.type == pygame.MOUSEBUTTONDOWN:
                self.pos = base.pos
                self.button = base.button
            elif self.type == pygame.KEYDOWN:
                self.key = base.key


class Events:
    is_testing = False

    def poll(self) -> Event:                            # NO-COV
        return Event(pygame.event.poll())

    def wait(self) -> Event:                            # NO-COV
        return Event(pygame.event.wait())

    def webbrowser_open(self, url: str) -> None:        # NO-COV
        pygame.display.iconify()
        try:
            webbrowser.open(url, True, True)
        except Exception:                               
            pass                                        # NO-COV

    def check_update(self, url: str) -> str:            # NO-COV
        with urllib.request.urlopen(url) as f:
            new_version_bytes = f.readline()
            return new_version_bytes.decode("ascii")
