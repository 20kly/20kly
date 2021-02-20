# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 

# Simple animation of map objects
# 
# I wrote this very late at night. It may well be total shit
# but it appears to work. I am stressed out and should probably 
# go to bed. 
#
# Main thing: you can't have surfaces in Draw_Obj because it
# has to be pickled. That's why they are hidden on the other
# side of the cache.


import pygame , math
from pygame.locals import *

import resource
from primitives import *



cache = dict()
frame = 0

class Draw_Obj:
    def __init__(self, img_name, grid_size):
        self.key = (img_name, grid_size)
        Make_Cache_Item(self.key)

    def Draw(self, output, gpos, sxsy):
        cache[ self.key ].Draw(output, gpos, sxsy)

def Flush_Draw_Obj_Cache():
    global cache
    cache = dict()

def Next_Frame():
    global frame
    frame += 1

def Make_Cache_Item(key):
    if ( cache.get(key, None) ):
        return  # Done already.

    class Real_Draw_Obj:
        def __init__(self, key):
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

        def Draw(self, output, gpos, sxsy):
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

    cache[ key ] = Real_Draw_Obj(key)

