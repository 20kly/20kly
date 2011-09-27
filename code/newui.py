# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


import pygame 
from pygame.locals import *

from colours import *
from primitives import *
import render, draw_obj, trig

LABEL_SIZE = 10
MENU_BORDER = 5
MENU_PADDING = 5

class Space_Item:
    def __init__(self, height):
        (self.width, self.height) = (1, height + MENU_PADDING)

    def Draw(self, output, rect):
        pass

    def Mouse_Move(self, ipos):
        pass

    def Mouse_Down(self):
        pass

class Label_Item(Space_Item):
    def __init__(self, text, colour):
        Space_Item.__init__(self, 0)
        self.text = text
        self.surface = render.Render(text, LABEL_SIZE, colour)
        (self.width, self.height) = self.surface.get_rect().size

    def Draw(self, output, rect):
        # Draw in centre of output rectangle
        r = self.surface.get_rect()
        r.center = rect.center
        output.blit(self.surface, r.topleft)

class Data_Label_Item(Label_Item):
    def __init__(self, text, colour, get_value_fn):
        Label_Item.__init__(self, text, colour)
        self.get_value_fn = get_value_fn

        # Reserve space for the label
        (w, h) = Get_Default_Size()
        self.width += (w * 5) / 4
        self.label_box_size = (w, h)

    def Draw(self, output, rect):
        # Draw label text on left hand side
        r = self.surface.get_rect()
        r.center = rect.center
        r.left = rect.left
        output.blit(self.surface, r.topleft)

        # Draw label area
        r2 = Rect((0, 0), self.label_box_size)
        r2.center = rect.center
        r2.right = rect.right
        pygame.draw.rect(output, BLACK, r2)

        # Obtain & draw label text
        (value_text, colour) = self.get_value_fn()
        surf = render.Render(value_text, LABEL_SIZE, colour)
        r3 = surf.get_rect()
        r3.center = r2.center
        r3.right = r2.right
        output.blit(surf, r3.topleft)

def Get_Default_Size():
    return render.Get_Size("FUTILE39", LABEL_SIZE)

class Bar_Item(Space_Item):
    def __init__(self, bg_colour, get_value_fn):
        Space_Item.__init__(self, 0)
        (self.width, self.height) = Get_Default_Size()

        self.get_value_fn = get_value_fn
        self.bg_colour = bg_colour

    def Draw(self, output, rect):
        # Blank the whole area
        pygame.draw.rect(output, self.bg_colour, rect)

        # Obtain value
        (value, max_value, colour) = self.get_value_fn()

        if max_value <= 0:
            # Scale is invalid, do not draw bar
            return 

        # Drawing the scale
        limit = rect.left + min(
                    (value * rect.width) / max_value, rect.width - 4) - 1
        x = 3 + rect.left
        y1 = rect.top + 2
        y2 = rect.bottom - 3
        while x < limit:
            pygame.draw.line(output, colour, (x, y1), (x, y2))
            x += 2

class Button_Group_Item(Space_Item):
    def __init__(self, button_list):
        Space_Item.__init__(self, 0)
        (self.width, self.height) = Get_Default_Size()

        self.button_margin = self.height
        self.button_size = self.height * 3
        self.width = ((self.button_size * len(button_list)) +
                    self.button_margin * (len(button_list) - 1))
        self.height = self.button_size
        self.mouse_over = None
        self.buttons = []

        x = 0
        for b in button_list:
            assert isinstance(b, Button_Item)
            r = Rect(x, 0, self.button_size, self.button_size)
            x += self.button_size + self.button_margin
            self.buttons.append((r, b))
            b.Set_Size(self.button_size)

    def Draw(self, output, rect):
        for (r, b) in self.buttons:
            r2 = Rect(r)
            r2.left += rect.left
            r2.top += rect.top

            if self.mouse_over == b:
                pygame.draw.rect(output, GREY, r2)

            b.Draw(output, r2)

            if self.mouse_over == b:
                pygame.draw.rect(output, WHITE, r2, 1)

    def Mouse_Move(self, ipos):

        self.mouse_over = None

        for (r, b) in self.buttons:
            if r.collidepoint(ipos):
                self.mouse_over = b
                return

    def Mouse_Down(self):
        if self.mouse_over != None:
            self.mouse_over.click_fn()
            self.mouse_over = None
    
class Button_Item:
    def __init__(self, src_image_name, src_image_rect, click_fn):
        self.src_image_name = src_image_name
        self.src_image_rect = src_image_rect
        self.draw_obj = None
        self.click_fn = click_fn

    def Set_Size(self, w):
        self.draw_obj = draw_obj.Screen_Draw_Obj(
                self.src_image_name, self.src_image_rect, w)

    def Draw(self, output, rect):
        self.draw_obj.Draw(output, rect.topleft)

class Popup_Menu:
    def __init__(self, bg_colour, border_colour):
        (self.width, self.height) = (
                render.Get_Size("This is the menu width", LABEL_SIZE))
        self.height = 0
        self.contents = []
        self.rect = Rect(0, 0, self.width, 1)
        self.bg_colour = bg_colour
        self.border_colour = border_colour

    def Add_To_Layout(self, item):
        assert isinstance(item, Space_Item)
        self.width = max(item.width, self.width)
        self.height += item.height + MENU_PADDING
        self.contents.append(item)
        self.rect.size = (self.width + (MENU_BORDER * 2),
                        self.height + (MENU_BORDER * 2) - MENU_PADDING)
        self.last_item = None

    def Draw(self, output):
        r = self.rect
        pygame.draw.rect(output, self.bg_colour, r)
        pygame.draw.rect(output, self.border_colour, r, 2)
        (x, y) = r.topleft
        x += MENU_BORDER
        y += MENU_BORDER
        w = self.width

        for item in self.contents:
            h = item.height
            item.Draw(output, Rect(x, y, w, h))
            y += h + MENU_PADDING

    def Mouse_Move(self, spos):
        r = self.rect
        self.last_item = None

        for item in self.contents:
            item.Mouse_Move((-1, -1))

        if not r.collidepoint(spos):
            return 

        (sx, sy) = spos
        sx -= r.left + MENU_BORDER
        sy -= r.top + MENU_BORDER

        if not ((0 <= sx < self.width) and (0 <= sy)):
            return


        for item in self.contents:
            h = item.height
            if sy < h:
                item.Mouse_Move((sx, sy))
                self.last_item = item
                return

            sy -= h + MENU_PADDING

    def Mouse_Down(self):
        if self.last_item != None:
            self.last_item.Mouse_Down()

        self.last_item = None
        
    def Place_Menu(self, centre_spos, ui):
        # Position the menu rectangle appropriately; this
        # means on-screen and overlapping as few things as
        # possible.
        (x0, y0) = centre_spos

        grid_size = Get_Grid_Size()
        tests = 12
        delta = 360 / tests
        best_score = -LARGE_NUMBER
        angle = 180 - delta
        choose = ui.screen_rect.center
        # Default is hopefully never actually used.

        for i in xrange(tests):
            (x1, y1) = trig.Angle(angle, POPUP_RADIUS, (x0, y0))
            self.rect.center = (x1, y1)
            self.rect.clamp_ip(ui.screen_rect)

            score = 0

            if self.rect.center != (x1, y1):
                score -= 100    # Rectangle moved by screen border

            if self.rect.collidepoint(centre_spos):
                score -= 1000   # Rectangle includes selection point

            for y2 in xrange(self.rect.top,
                        self.rect.bottom, grid_size):
                for x2 in xrange(self.rect.left,
                            self.rect.right, grid_size):
        
                    if ui.Get_Item(Scr_To_Grid((x2, y2)), False) != None:
                        score -= 1 # Rectangle is above something
  
            if score > best_score:
                best_score = score
                choose = self.rect.center

            angle += delta

        # Pick the best site for placement
        self.rect.center = choose
            





        


