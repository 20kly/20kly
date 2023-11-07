#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame, webbrowser, urllib.request
from .game_types import *
from .primitives import *
from . import mail, config, compatibility


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
        self.gain = 0
        self.state = 0

        if base is not None: # NO-COV
            self.type = base.type
            if ((self.type == pygame.MOUSEMOTION)
            or (self.type == pygame.MOUSEBUTTONUP)
            or (self.type == pygame.MOUSEBUTTONDOWN)):
                (x, y) = base.pos
                if parent is not None:
                    x -= parent.left_margin
                    y -= parent.top_margin
                self.pos = (x, y)
                if self.type != pygame.MOUSEMOTION:
                    self.button = base.button
            elif self.type == pygame.KEYDOWN:
                self.key = base.key
            elif self.type == pygame.ACTIVEEVENT and hasattr(base, "gain") and hasattr(base, "state"):
                self.gain = base.gain
                self.state = base.state
            elif self.type == pygame.VIDEORESIZE:
                compatibility.last_resize = base.size


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

        if compatibility.PYGAME_TWO:
            # pygame 2: the display surface doesn't change
            (width, height) = screen.get_rect().size
        else:
            # pygame 1: must recreate the display surface
            (width, height) = compatibility.last_resize
            self.old_size = (0, 0)

        # Recreate display surface if necessary:
        # (1) screen was resized and is now too small
        # (2) not using pygame 2.x
        if (width < MINIMUM_WIDTH) or (height < MINIMUM_HEIGHT) or (not compatibility.PYGAME_TWO):
            width = max(width, MINIMUM_WIDTH)
            height = max(height, MINIMUM_HEIGHT)
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            (width, height) = screen.get_rect().size

            # just in case it didn't really resize appropriately
            # we just assume the minimum size
            width = max(width, MINIMUM_WIDTH)
            height = max(height, MINIMUM_HEIGHT)

        new_size = (width, height)
        if new_size != self.old_size:
            # size has changed
            screen.fill((0, 0, 0))
            self.old_size = new_size
            self.left_margin = 0
            self.top_margin = 0

        aspect = width / height
        error = aspect - EXPECTED_ASPECT_RATIO
        if error > 0.01:
            # widescreen - black bars at the sides
            true_width = int(math.floor(height * EXPECTED_ASPECT_RATIO))
            self.left_margin = (width - true_width) // 2
            assert self.left_margin >= 0
            screen = screen.subsurface(pygame.Rect(self.left_margin, 0,
                    true_width, height).clip(screen.get_rect()))
            width = true_width

        elif error < -0.01:
            # phone screen - black bars at the top/bottom
            true_height = int(math.floor(width / EXPECTED_ASPECT_RATIO))
            self.top_margin = (height - true_height) // 2
            assert self.top_margin >= 0
            screen = screen.subsurface(pygame.Rect(0, self.top_margin,
                    width, true_height).clip(screen.get_rect()))
            height = true_height

        # Notify other components of size change
        mail.Set_Screen_Height(height)
        config.cfg.width = width
        config.cfg.height = height

        return screen
