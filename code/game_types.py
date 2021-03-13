#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
import typing

from typing import List, Dict, Tuple, Union, Optional
from .primitives import MenuCommand

SurfaceType = pygame.surface.Surface
Colour = Tuple[int, int, int]
Colour4 = Tuple[int, int, int, int]
BarMeterStatTuple = Tuple[int, Colour, int, Colour]
StatTuple = Tuple[Optional[Colour], Optional[int], Union[BarMeterStatTuple, str]]
SurfacePosition = Tuple[int, int]
FloatSurfacePosition = Tuple[float, float]
GridPosition = Tuple[int, int]
FloatGridPosition = Tuple[float, float]
DrawObjKey = Tuple[str, int]
RectType = pygame.rect.Rect
UpdateAreaMethod = typing.Callable[[RectType], None]
MenuItem = Tuple[Optional[MenuCommand], Optional[str], List[int]]
ClockType = typing.Any
ControlRectType = Tuple[MenuCommand, RectType]
NextParticleType = Tuple[FloatSurfacePosition, Colour4]
FloatGridLine = Tuple[FloatGridPosition, FloatGridPosition]
GridLine = Tuple[GridPosition, GridPosition]
VersionType = Tuple[int, int, int]

