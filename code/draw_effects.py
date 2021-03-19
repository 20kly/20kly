#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#
#

import pygame

from . import resource
from .primitives import *
from .game_types import *

__screen_height = MINIMUM_HEIGHT


def Tile_Texture(output: SurfaceType, name: Images, rect: RectType) -> None:
    cr = output.get_clip()
    output.set_clip(rect)

    img = Scale_Image(resource.Load_Image(name))
    img_r = img.get_rect()
    for x in range(0, rect.width, img_r.width):
        for y in range(0, rect.height, img_r.height):
            output.blit(img, (x + rect.left, y + rect.top))

    output.set_clip(cr)

def Edge_Effect(output: SurfaceType, rect: RectType) -> None:
    bolt = Scale_Image(resource.Load_Image(Images.bolt))
    margin = (2 * __screen_height) // MINIMUM_HEIGHT
    for x in [ rect.left + margin , rect.right - ( margin + 3 ) ]:
        for y in [ rect.top + margin , rect.bottom - ( margin + 3 ) ]:
            output.blit(bolt, (x,y))

def Line_Edging(screen: SurfaceType, r: RectType, deflate: bool) -> None:
    margin = (2 * __screen_height) // MINIMUM_HEIGHT
    for c in [ (75, 63, 31), (125, 99, 30), (160, 120, 40), (75, 63, 31), (0, 0, 0) ]:
        pygame.draw.rect(screen, c, r, margin // 2)
        if ( deflate ):
            r = r.inflate(-margin, -margin)
        else:
            r = r.inflate(margin, margin)

def Scale_Image(img: SurfaceType) -> SurfaceType:
    (img_width, img_height) = img.get_rect().size
    img_width = (img_width * __screen_height) // MINIMUM_HEIGHT
    img_height = (img_height * __screen_height) // MINIMUM_HEIGHT
    return pygame.transform.smoothscale(img, (img_width, img_height))

def Get_Margin(size_at_768: int) -> int:
    return (size_at_768 * __screen_height) // MINIMUM_HEIGHT

def Set_Screen_Height(height: int) -> None:
    global __screen_height
    __screen_height = height
