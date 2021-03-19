#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# A very lightweight menu system.

import pygame, enum


from . import stats, draw_effects, resource, render, sound, events, config
from .game_types import *
from .primitives import *


class Menu:
    def __init__(self, menu_options: List[MenuItem], force_width=0) -> None:
        self.options = menu_options

        self.control_rects: List[ControlRectType] = []
        self.hover: Optional[MenuCommand] = None
        self.bbox: RectType = pygame.Rect(0, 0, 1, 1)

        self.output_size = (0, 0)
        self.selection: Optional[MenuCommand] = None
        self.update_required = True
        self.force_width = force_width
        self.Resize_Surface()

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
                    sound.FX(Sounds.click_s)
                return

    def Mouse_Down(self, spos: SurfacePosition) -> None:
        self.Mouse_Move(spos)
        if ( self.hover is not None ):
            self.selection = self.hover
            sound.FX(Sounds.click)

    def Key_Press(self, k: int) -> None:
        for (num, name, hotkeys) in self.options:
            if (( hotkeys is not None ) and ( k in hotkeys )):
                self.selection = num
                self.update_required = True
                sound.FX(Sounds.click)
                return

    def Force_Full_Update(self) -> None:
        self.update_required = True
        self.output_size = (0, 0)

    def Resize_Surface(self) -> None:
        self.update_required = True

        # estimate of width and height for first attempt at drawing
        width_hint = height_hint = 10

        if self.force_width > 0:
            width_hint = self.force_width

        # Two attempts at drawing required.
        # First we compute the size of the bounding box
        (_, _, (width_hint, height_hint)) = self.__Draw((width_hint, height_hint))

        width_hint = max(width_hint, 150)
        if self.force_width > 0:
            width_hint = self.force_width

        # Second step is to draw into the bounding box
        (self.surf_store, self.control_rects, _) = self.__Draw((width_hint, height_hint))
        self.bbox = pygame.Rect(0, 0, width_hint, height_hint)

    def Draw(self, output: SurfaceType, centre: Optional[SurfacePosition] = None) -> None:

        # If the output window size has changed, recompute the size of the menu
        if output.get_rect().size != self.output_size:
            self.output_size = output.get_rect().size
            self.Resize_Surface()

        # Only redraw the menu if an update is required
        if not self.update_required:
            return

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

        draw_effects.Tile_Texture(surf, Images.i006metal, surf.get_rect())

        margin = draw_effects.Get_Margin(8)
        w = bbox.width - ( margin * 2 )
        th = None
        y = margin + bbox.top
        control_rects: List[ControlRectType] = []
        max_width = 0
        first_item = True

        for (num, name, hotkeys) in self.options:
            if ( name is None ): # a gap
                if ( first_item ):
                    img = draw_effects.Scale_Image(resource.Load_Image(Images.header))
                    img_r = img.get_rect()
                    img_r.center = bbox.center
                    img_r.top = y
                    surf.blit(img, img_r.topleft)
                    draw_effects.Edge_Effect(surf, img_r)
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

            draw_effects.Tile_Texture(surf, Images.greenrust, r)
            draw_effects.Edge_Effect(surf, r)
            if num is not None:
                self.Enhancement_Interface(surf, num, r, margin)

            surf.blit(txt, (x,y + margin - 1))
            y += th + margin

            if num is not None:
                control_rects.append((num, r))

            first_item = False


        # Finalise drawing
        draw_effects.Line_Edging(surf, bbox, True)

        return (surf, control_rects, (max_width, y))


    def Justify(self, width: int, text_width: int) -> int:
        return ( width - text_width ) // 2

    def Enhancement_Interface(self, surf: SurfaceType,
            num: MenuCommand, rect: RectType, margin: int) -> None:
        pass

# Menu plus pictures!
class Enhanced_Menu(Menu):
    def __init__(self, menu_options: List[MenuItem],
                 pictures: Dict[MenuCommand, Images], force_width=0):
        self.pictures = pictures
        Menu.__init__(self, menu_options, force_width)

    def Enhancement_Interface(self, surf: SurfaceType,
            num: MenuCommand, rect: RectType, margin: int) -> None:
        if ( self.pictures.get( num, None ) ):
            img = draw_effects.Scale_Image(resource.Load_Image(self.pictures[num]))
            img_r = img.get_rect()
            img_r.center = rect.center
            img_r.left = rect.left + margin
            surf.blit(img, img_r.topleft)


# This menu offers an option to turn the sound on or off
# which is updated when clicked. The option isn't present if
# sound is disabled.
TOGGLE_SOUND = (MenuCommand.MUTE, "Turn Sound ...", [pygame.K_m])

class Toggle_Sound_Menu(Menu):
    def __init__(self, menu_options: List[MenuItem], force_width=0) -> None:
        self.options = menu_options[:]
        self.toggle_sound_index = self.options.index(TOGGLE_SOUND)

        if resource.Has_No_Sound():
            self.options.pop(self.toggle_sound_index)
            self.toggle_sound_index = -1
        else:
            self.Set_Sound_Item()

        Menu.__init__(self, self.options, force_width)

    def Mouse_Down(self, spos: SurfacePosition) -> None:
        Menu.Mouse_Down(self, spos)
        self.Check_Selection()

    def Key_Press(self, k: int) -> None:
        Menu.Key_Press(self, k)
        self.Check_Selection()

    def Check_Selection(self) -> None:
        if self.selection == TOGGLE_SOUND[0]:
            config.cfg.mute = not config.cfg.mute
            sound.FX(Sounds.click)
            self.Set_Sound_Item()
            self.Force_Full_Update()
            self.selection = None

    def Set_Sound_Item(self) -> None:
        if config.cfg.mute:
            text = "Turn Sound On"
        else:
            text = "Turn Sound Off"

        assert self.toggle_sound_index >= 0
        self.options[self.toggle_sound_index] = (
                TOGGLE_SOUND[0], text, TOGGLE_SOUND[2])


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
