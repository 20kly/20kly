#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import game_types, primitives


class Grid:
    def __init__(self) -> None:
        self.Set_Grid_Size(10)

    def Scr_To_Grid(self, xy: game_types.SurfacePosition) -> game_types.GridPosition:
        (x,y) = xy
        return (x // self.size, y // self.size)

    def Grid_To_Scr(self, xy: game_types.GridPosition) -> game_types.SurfacePosition:
        (x,y) = xy
        return (( x * self.size ) + self.h_size,
                ( y * self.size ) + self.h_size )

    def Float_Grid_To_Scr(self, xy: game_types.FloatGridPosition) -> game_types.FloatSurfacePosition:
        (x,y) = xy
        return (( x * self.size ) + self.h_size,
                ( y * self.size ) + self.h_size )

    def Grid_To_Scr_Rect(self, xy: game_types.GridPosition) -> game_types.RectType:
        (x,y) = xy
        (cx,cy) = Grid_To_Scr((x,y))
        return pygame.Rect(cx - self.h_size_1, cy - self.h_size_1,
                self.size_1, self.size_1)

    def Set_Grid_Size(self, sz: int) -> None:
        assert type(sz) == int
        self.size = sz
        self.size_1 = sz - 1
        self.h_size = sz // 2
        self.h_size_1 = self.h_size - 1

    def Get_Grid_Size(self) -> int:
        return self.size


__grid = Grid()
Grid_To_Scr_Rect = __grid.Grid_To_Scr_Rect
Grid_To_Scr = __grid.Grid_To_Scr
Float_Grid_To_Scr = __grid.Float_Grid_To_Scr
Scr_To_Grid = __grid.Scr_To_Grid
Get_Grid_Size = __grid.Get_Grid_Size

def Set_Screen_Height(height: int) -> None:
    (w, h) = primitives.GRID_SIZE
    assert w == h
    __grid.Set_Grid_Size(height // h)

