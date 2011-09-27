# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 



import pygame
from pygame.locals import *

import resource
from primitives import *



cache = dict()
frame = 0

class Grid_Draw_Obj:
    def __init__(self, src_image_name, src_image_rect, grid_size):
        if src_image_rect != None:
            src_image_rect = tuple(src_image_rect) # x,y,w,h

        self.key = (src_image_name, src_image_rect, grid_size)

    def Draw(self, output, gpos, spos):
        item = cache.get(self.key, None)
        if item == None:
            item = Make_Cache_Item(self.key)
        item.Draw_On_Grid(output, gpos, spos)

class Screen_Draw_Obj:
    def __init__(self, src_image_name, src_image_rect, width):
        if src_image_rect != None:
            src_image_rect = tuple(src_image_rect) # x,y,w,h

        self.key = (src_image_name, src_image_rect, -width)

    def Draw(self, output, spos):
        item = cache.get(self.key, None)
        if item == None:
            item = Make_Cache_Item(self.key)
        item.Draw_At_XY(output, spos)

def Flush_Draw_Obj_Cache():
    global cache
    cache = dict()

def Next_Frame():
    global frame
    frame += 1

class Real_Draw_Obj:
    def __init__(self, key):
        (src_image_name, src_image_rect, grid_size) = key

        # Load the complete image file
        img = resource.Load_Image(src_image_name)

        # Crop out the required rectangle if any
        if src_image_rect != None:
            assert type(src_image_rect) == tuple
            assert len(src_image_rect) == 4 # x,y,w,h
            img = img.subsurface(Rect(src_image_rect))

        if grid_size >= 0:
            # Rescale for grid
            new_size = Get_Grid_Size() * grid_size
            grid_rect = Rect(0, 0, new_size, new_size)
            self.grid_mode = True
        else:
            grid_rect = Rect(0, 0, -grid_size, -grid_size)
            self.grid_mode = False

        img_rect = img.get_rect().fit(grid_rect)
        img  = pygame.transform.scale(img, img_rect.size)

        # Calculate offsets
        img_rect.center = (0, 0)
        self.offset_x = img_rect.left
        self.offset_y = img_rect.top

        # Make frames
        self.frames = []
        if self.grid_mode:
            #for c in [ 0, 0, 50, 100, 150, 200, 250, 250, 150 ]:
            #    self.frames.append(self.__Colour_Substitute(c, img))
            self.frames.append(img)
        else:
            self.frames.append(img)

    def Draw_On_Grid(self, output, gpos, (sx, sy)):
        global frame

        assert self.grid_mode 
        (x,y) = Grid_To_Scr(gpos)
        x += self.offset_x - sx
        y += self.offset_y - sy
        output.blit(self.frames[ ( frame / 2 ) % len(self.frames) ], (x,y))

    def Draw_At_XY(self, output, (x, y)):
        global frame

        assert not self.grid_mode 
        output.blit(self.frames[ ( frame / 2 ) % len(self.frames) ], (x,y))

    def __Colour_Substitute(self, sub, image):
        out = image.copy()
        (w,h) = image.get_rect().bottomright

        for y in xrange(h):
            for x in xrange(w):
                (r,g,b,a) = out.get_at((x,y))
                if (( r > 200 ) and ( g < 30 ) and ( b < 30 )): # threshold
                    out.set_at((x,y), (sub, 0, 0, a))
        return out

def Make_Cache_Item(key):
    item = cache.get(key, None)
    if item == None:
        item = cache[ key ] = Real_Draw_Obj(key)

    return item


