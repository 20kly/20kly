#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame, webbrowser, urllib.request
from .game_types import *
from .primitives import *


class Event:
    def __init__(self,
                 base: Optional[pygame.event.Event] = None,
                 parent: "Optional[Events]" = None,
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
            if (self.type == pygame.MOUSEMOTION) or (self.type == pygame.MOUSEBUTTONDOWN):
                (x, y) = base.pos
                if parent is not None:
                    x -= parent.left_margin
                    y -= parent.top_margin
                self.pos = (x, y)
                if self.type == pygame.MOUSEBUTTONDOWN:
                    self.button = base.button
            elif self.type == pygame.KEYDOWN:
                self.key = base.key


class Events:
    is_testing = False
    old_size: SurfacePosition = (0, 0)
    left_margin = 0
    top_margin = 0

    def poll(self) -> Event:                            # NO-COV
        return Event(pygame.event.poll(), self)

    def wait(self) -> Event:                            # NO-COV
        return Event(pygame.event.wait(), self)

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

    def resurface(self) -> SurfaceType:                 # NO-COV
        screen = pygame.display.get_surface()
        (width, height) = new_size = screen.get_rect().size

        if (width < MINIMUM_WIDTH) or (height < MINIMUM_HEIGHT):
            # Screen was resized and is now too small
            res = (max(width, MINIMUM_WIDTH), max(height, MINIMUM_HEIGHT))
            screen = pygame.display.set_mode(res, pygame.RESIZABLE)
            (width, height) = screen.get_rect().size

        if new_size != self.old_size:
            # size has changed
            screen.fill((0, 0, 0))
            self.old_size = new_size
            self.left_margin = 0
            self.right_margin = 0

        aspect = width / height
        error = aspect - EXPECTED_ASPECT_RATIO
        if error > 0.01:
            # widescreen - black bars at the sides
            true_width = int(math.floor(height * EXPECTED_ASPECT_RATIO))
            self.left_margin = (width - true_width) // 2
            assert self.left_margin >= 0
            screen = screen.subsurface(pygame.Rect(self.left_margin, 0, true_width, height))

        elif error < -0.01:
            # phone screen - black bars at the top/bottom
            true_height = int(math.floor(width / EXPECTED_ASPECT_RATIO))
            self.top_margin = (height - true_height) // 2
            assert self.top_margin >= 0
            screen = screen.subsurface(pygame.Rect(0, self.top_margin, width, true_height))

        return screen

