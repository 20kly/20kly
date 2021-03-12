#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

# Simple animation of map objects


import pygame, math


from . import resource
from .primitives import *
from .game_types import *
from .grid import Get_Grid_Size, Grid_To_Scr


class Abstract_Draw_Obj:
    def Draw(self, output: SurfaceType, gpos: GridPosition, sxsy: SurfacePosition) -> None:
        pass  # NO-COV

cache: Dict[DrawObjKey, Abstract_Draw_Obj] = dict()
frame = 0

class Draw_Obj(Abstract_Draw_Obj):
    def __init__(self, img_name: str, grid_size: int) -> None:
        Abstract_Draw_Obj.__init__(self)
        self.key = (img_name, grid_size)

    def Draw(self, output: SurfaceType, gpos: GridPosition, sxsy: SurfacePosition) -> None:
        item = cache.get(self.key, None)
        if item is None:
            cache[self.key] = item = Make_Cache_Item(self.key)
        item.Draw(output, gpos, sxsy)

def Flush_Draw_Obj_Cache() -> None:
    global cache
    cache.clear()

def Next_Frame() -> None:
    global frame
    frame += 1

def Make_Cache_Item(key: DrawObjKey) -> Abstract_Draw_Obj:
    class Real_Draw_Obj(Abstract_Draw_Obj):
        def __init__(self, key: DrawObjKey) -> None:
            Abstract_Draw_Obj.__init__(self)
            (img_name, grid_size) = key

            img = resource.Load_Image(img_name)
            (w, h) = img.get_rect().bottomright
            new_width = Get_Grid_Size() * grid_size
            new_height = ( new_width * h ) // w
            assert type(Get_Grid_Size()) == int
            assert type(grid_size) == int
            assert type(new_width) == int
            assert type(new_height) == int

            img = pygame.transform.scale(img, (new_width, new_height))

            r = img.get_rect()
            r.center = (0,0)
            self.offset_x = r.left
            self.offset_y = r.top
            self.frames = []
            for c in [ 0, 0, 50, 100, 150, 200, 250, 250, 150 ]:
                self.frames.append(self.__Colour_Substitute(c, img))

        def Draw(self, output: SurfaceType, gpos: GridPosition, sxsy: SurfacePosition) -> None:
            (sx, sy) = sxsy
            global frame

            (x,y) = Grid_To_Scr(gpos)
            x += self.offset_x - sx
            y += self.offset_y - sy
            output.blit(self.frames[ ( frame // 2 ) % len(self.frames) ], (x,y))

        def __Colour_Substitute(self, sub, image):
            out = image.copy()
            (w,h) = image.get_rect().bottomright

            for y in range(h):
                for x in range(w):
                    (r,g,b,a) = out.get_at((x,y))
                    if (( r > 200 ) and ( g < 30 ) and ( b < 30 )): # threshold
                        out.set_at((x,y), (sub, 0, 0, a))
            return out

    return Real_Draw_Obj(key)

