#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

import pygame
from . import game_types

__grid_size = 0
__grid_size_1 = 0
__h_grid_size = 0
__h_grid_size_1 = 0

def Scr_To_Grid(xy: game_types.SurfacePosition) -> game_types.GridPosition:
    (x,y) = xy
    return (x // __grid_size, y // __grid_size)

def Grid_To_Scr(xy: game_types.GridPosition) -> game_types.SurfacePosition:
    (x,y) = xy
    return (( x * __grid_size ) + __h_grid_size,
            ( y * __grid_size ) + __h_grid_size )

def Float_Grid_To_Scr(xy: game_types.FloatGridPosition) -> game_types.FloatSurfacePosition:
    (x,y) = xy
    return (( x * __grid_size ) + __h_grid_size,
            ( y * __grid_size ) + __h_grid_size )

def Grid_To_Scr_Rect(xy: game_types.GridPosition) -> game_types.RectType:
    (x,y) = xy
    (cx,cy) = Grid_To_Scr((x,y))
    return pygame.Rect(cx - __h_grid_size_1, cy - __h_grid_size_1,
            __grid_size_1, __grid_size_1)

def Set_Grid_Size(sz: int) -> None:
    global __grid_size, __grid_size_1, __h_grid_size, __h_grid_size_1
    assert type(sz) == int
    __grid_size = sz
    __grid_size_1 = sz - 1
    __h_grid_size = sz // 2
    __h_grid_size_1 = __h_grid_size - 1

def Get_Grid_Size() -> int:
    return __grid_size

Set_Grid_Size(10)

