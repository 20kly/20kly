#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# A very lightweight menu system.

import pygame


from . import stats, extra, resource, render, sound, events
from .game_types import *


class Menu:
    def __init__(self, menu_options: List[MenuItem], force_width=0) -> None:
        self.options = menu_options

        self.control_rects: List[ControlRectType] = []
        self.hover: Optional[MenuCommand] = None
        self.bbox: RectType

        self.selection: Optional[MenuCommand] = None
        self.update_required = True

        width_hint = height_hint = 10

        if ( force_width > 0 ):
            width_hint = force_width

        # Two attempts at drawing required.
        (_, _, (width_hint, height_hint)) = self.__Draw((width_hint, height_hint))

        if ( width_hint < 150 ):
            width_hint = 150
        if ( force_width > 0 ):
            width_hint = force_width

        (self.surf_store, self.control_rects,
            _) = self.__Draw((width_hint, height_hint))

        self.bbox = pygame.Rect(0, 0, width_hint, height_hint)

    def Get_Command(self) -> Optional[MenuCommand]:
        return self.selection

    def Select(self, snum: Optional[MenuCommand]) -> None:
        self.update_required = True
        self.selection = snum

    def Mouse_Move(self, spos: Optional[SurfacePosition]) -> None:
        if (( spos is None )
        or ( not self.bbox.collidepoint(spos) )):
            self.hover = None
            return

        self.update_required = True
        (x,y) = spos

        old_sel = self.hover
        self.hover = None
        x -= self.bbox.left
        y -= self.bbox.top
        for (num, r) in self.control_rects:
            assert num is not None
            if ( r.collidepoint(x,y) ):
                self.hover = num
                if ( old_sel != self.hover ):
                    sound.FX("click_s")
                return

    def Mouse_Down(self, spos: SurfacePosition) -> None:

        self.Mouse_Move(spos)
        if ( self.hover is not None ):
            self.selection = self.hover
            sound.FX("click")

    def Key_Press(self, k: int) -> None:
        for (num, name, hotkeys) in self.options:
            if (( hotkeys is not None ) and ( k in hotkeys )):
                self.selection = num
                self.update_required = True
                sound.FX("click")
                return

    def Draw(self, output: SurfaceType,
             centre: Optional[SurfacePosition] = None) -> None:
        if ( self.update_required ):
            self.update_required = False

            if ( centre is None ):
                self.bbox.center = output.get_rect().center
            else:
                self.bbox.center = centre

            self.bbox.clamp_ip(output.get_rect())

            output.blit(self.surf_store, self.bbox.topleft)

            for (num, r) in self.control_rects:
                assert num is not None
                r = pygame.Rect(r)
                r.top += self.bbox.top
                r.left += self.bbox.left
                if ( num == self.selection ):
                    pygame.draw.rect(output, (255, 255, 255), r, 1)
                elif ( num == self.hover ):
                    pygame.draw.rect(output, (0, 180, 0), r, 1)


    def __Draw(self, width_height_hint: SurfacePosition) -> Tuple[
            SurfaceType, List[ControlRectType], SurfacePosition]:
        (width_hint, height_hint) = width_height_hint
        surf = pygame.Surface((width_hint, height_hint))
        bbox = pygame.Rect(0, 0, width_hint, height_hint)

        extra.Tile_Texture(surf, "006metal.jpg", surf.get_rect())

        margin = 8
        w = bbox.width - ( margin * 2 )
        th = None
        y = margin + bbox.top
        control_rects: List[ControlRectType] = []
        max_width = 0
        first_item = True

        for (num, name, hotkeys) in self.options:
            if ( name is None ): # a gap
                if ( first_item ):
                    img = resource.Load_Image("header.jpg")
                    img_r = img.get_rect()
                    img_r.center = bbox.center
                    img_r.top = y
                    surf.blit(img, img_r.topleft)
                    extra.Edge_Effect(surf, img_r)
                    max_width = img_r.width + ( margin * 2 )
                    y += img_r.height

                y += margin * 2
                continue

            txt = render.Render(name, 18, (50,200,20), (200,200,0))
            if ( th is None ):
                th = txt.get_rect().height + ( margin * 2 )
            tw = txt.get_rect().width + ( margin * 2 )
            if ( tw > max_width ):
                max_width = tw

            x = bbox.left + margin
            r = pygame.Rect(x,y,w,th)
            x += self.Justify(w,txt.get_rect().width)

            extra.Tile_Texture(surf, "greenrust.jpg", r)
            extra.Edge_Effect(surf, r)
            if num is not None:
                self.Enhancement_Interface(surf, num, r, margin)

            surf.blit(txt, (x,y + margin - 1))
            y += th + margin

            if num is not None:
                control_rects.append((num, r))

            first_item = False


        # Finalise drawing
        extra.Line_Edging(surf, bbox, True)

        return (surf, control_rects, (max_width, y))


    def Justify(self, width: int, text_width: int) -> int:
        return ( width - text_width ) // 2

    def Enhancement_Interface(self, surf: SurfaceType,
            num: MenuCommand, rect: RectType, margin: int) -> None:
        pass

# Menu plus pictures!
class Enhanced_Menu(Menu):
    def __init__(self, menu_options: List[MenuItem],
                 pictures: Dict[MenuCommand, str], force_width=0):
        self.pictures = pictures
        Menu.__init__(self, menu_options, force_width)

    def Enhancement_Interface(self, surf: SurfaceType,
            num: MenuCommand, rect: RectType, margin: int) -> None:
        if ( self.pictures.get( num, None ) ):
            img = resource.Load_Image( self.pictures[ num ] )
            img_r = img.get_rect()
            img_r.center = rect.center
            img_r.left = rect.left + margin
            surf.blit(img, img_r.topleft)


def Simple_Menu_Loop(screen: SurfaceType, current_menu: Menu,
                     xy: SurfacePosition, event: events.Events) -> Tuple[bool, Optional[MenuCommand]]:
    (x,y) = xy
    cmd = None
    quit = False

    while (( cmd is None ) and not quit ):
        current_menu.Draw(screen, (x,y))
        pygame.display.flip()

        e = event.wait()
        while ( e.type != pygame.NOEVENT ):
            if e.type == pygame.QUIT:
                quit = True
            elif ( e.type == pygame.MOUSEBUTTONDOWN ):
                current_menu.Mouse_Down(e.pos)
            elif ( e.type == pygame.MOUSEMOTION ):
                current_menu.Mouse_Move(e.pos)
            elif e.type == pygame.KEYDOWN:
                current_menu.Key_Press(e.key)
            elif e.type == pygame.VIDEORESIZE:
                return (False, None)

            e = event.poll()

        cmd = current_menu.Get_Command()
        current_menu.Select(None) # consume

    return (quit, cmd)



