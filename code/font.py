#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame
from . import resource
from .game_types import *
from .primitives import *

POINTS_TO_PIXELS = 1.2

class Font:
    def __init__(self) -> None:
        self.point_cache: Dict[int, pygame.font.Font] = dict()
        self.pixel_cache: Dict[int, pygame.font.Font] = dict()
        self.screen_height = MINIMUM_HEIGHT

    def Get_Font_Point_Size(self, point_size: int) -> pygame.font.Font:
        """The size of the font is specified in points: the resulting font
        pixel size depends on the font. For the font used here, the
        typical pixel size is POINTS_TO_PIXELS more than the point size."""
        obj = self.point_cache.get(point_size, None)
        if obj is not None:
            return obj

        self.point_cache[point_size] = obj = resource.Load_Font(point_size)
        return obj

    def Get_Font_Pixel_Size(self, desired_pixel_size: int) -> pygame.font.Font:
        """The size of the font is specified in pixels; the resulting font
        should have this pixel size, +/- 1 pixel."""

        obj = self.pixel_cache.get(desired_pixel_size, None)
        if obj is not None:
            return obj

        # estimate min/max bounds on the point size
        max_point_size = max(5, int(desired_pixel_size * 2.0 / POINTS_TO_PIXELS))
        min_point_size = max(5, int(desired_pixel_size * 0.5 / POINTS_TO_PIXELS))
        true_pixel_size = 0

        while max_point_size >= min_point_size:
            try_point_size = (max_point_size + min_point_size) // 2
            obj = self.Get_Font_Point_Size(try_point_size)
            s = obj.render(TITLE, True, (255, 255, 255))
            true_pixel_size = s.get_rect().height
            self.pixel_cache[true_pixel_size] = obj

            if true_pixel_size == desired_pixel_size:
                # font size is just right
                break
            elif true_pixel_size > desired_pixel_size:
                # font is too big
                max_point_size = try_point_size - 1
            else:
                # font is too small
                min_point_size = try_point_size + 1

        # Got the best font size for this pixel size
        assert obj is not None
        self.pixel_cache[desired_pixel_size] = obj
        return obj

    def Get_Font_Legacy_Size(self, legacy_size: int) -> pygame.font.Font:
        """The size of the font is specified in the legacy size used
        by 20kly, which is POINTS_TO_PIXELS times smaller than the
        desired pixel size, and also based on the assumption that the
        screen size is 1024 by 768."""
        return self.Get_Font_Pixel_Size(int(
                legacy_size * POINTS_TO_PIXELS * self.screen_height / MINIMUM_HEIGHT))

__font = Font()

def Get_Font_Pixel_Size(unscaled_size: int) -> pygame.font.Font:
    return __font.Get_Font_Pixel_Size(unscaled_size)

def Get_Font(legacy_size: int) -> pygame.font.Font:
    return __font.Get_Font_Legacy_Size(legacy_size)

def Set_Screen_Height(height: int) -> None:
    __font.screen_height = height
