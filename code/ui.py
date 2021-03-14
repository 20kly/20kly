#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# Do you believe in the users?

import pygame, random


from . import stats, menu, draw_obj, mail, particle, tutor
from .primitives import *
from .game_types import *
from . import game_random, network, resource, quiet_season, map_items
from .grid import Grid_To_Scr, Grid_To_Scr_Rect, Scr_To_Grid


class User_Interface:
    def __init__(self, net: "network.Network", demo: "game_random.Game_Random") -> None:
        self.net = net
        self.demo = demo
        self.control_menu: Optional[menu.Menu] = None
        self.update_area_list: List[RectType] = []
        self.stats_hash: int = 0
        self.selection: Optional[map_items.Building] = None
        self.mouse_pos: Optional[GridPosition] = None
        self.mode: Optional[MenuCommand] = MenuCommand.NEUTRAL


        self.Reset()
        self.blink = 0xff

        self.background: SurfaceType = pygame.Surface((1, 1))
        self.background.fill((0, 0, 0))

        self.steam_effect = particle.Make_Particle_Effect(particle.Steam_Particle)
        self.steam_effect_frame = 0


    def Update_Area(self, area: Optional[RectType]) -> None:
        if ( area is not None ):
            self.partial_update = True

            # pygame.Rect is rather good.

            if ( len(self.update_area_list) == 0 ):
                self.update_area_list = [area]
            else:
                ci = area.collidelist(self.update_area_list)
                if ( ci < 0 ):
                    # New area!
                    self.update_area_list.append(area)
                else:
                    # Area overlaps an existing area, which gets expanded.
                    self.update_area_list[ ci ].union_ip(area)

    def Update_Game(self) -> None:
        self.full_update = True

    def Update_All(self) -> None:
        # force redraw of game window
        self.Update_Game()

        # force redraw of (upper) stats window
        self.stats_hash = 0

        # force redraw of control menu
        self.control_menu = None

    def Draw_Game(self, output: SurfaceType,
                  season_fx: quiet_season.Quiet_Season,
                  paused: bool) -> None:
        blink = self.blink
        r: Optional[RectType]

        if ( season_fx.Is_Shaking() and not paused ):
            # Earthquake effect
            m = 6
            r = output.get_rect()
            r.left += random.randint(-m, m)
            r.top += random.randint(-m, m)
            r = output.get_rect().clip(r)
            output = output.subsurface(r)
            self.Update_Game()

        if ( self.net.dirty ):
            self.Update_Game()
            self.net.dirty = False

        if ( mail.Has_New_Mail() or tutor.Has_Changed() ):
            self.Update_Game() # force update

        # These things may not need to be redrawn
        # as they are never animated and can't be selected.

        if ( self.full_update ):
            output.blit(self.background,(0,0))

            self.__Update_Reset()

            for w in self.net.well_list:
                w.Draw(output)
                self.Add_Steam_Effect(output, w.pos)

        else:
            for u in self.update_area_list:
                output.blit(self.background, u.topleft, u)

            self.__Update_Reset()

            for w in self.net.well_list:
                w.Draw(output)
                self.Add_Steam_Effect(output, w.pos)


        # Everything else needs to be redrawn every turn.

        if ( self.selection is not None ):
            # highlight selection
            r = self.selection.Draw_Selected(output, (blink, blink, 0))
            self.Update_Area(r)

        for p in self.net.pipe_list:
            p.Draw(output)

        for n in self.net.node_list:
            n.Draw(output)
            if ( n.emits_steam ):
                self.Add_Steam_Effect(output, n.pos)


        season_fx.Draw(output, self.Update_Area)


        gpos = self.mouse_pos
        if ( gpos is not None ):
            if ( self.mode == MenuCommand.BUILD_NODE ):
                # could put a node here.
                r = Grid_To_Scr_Rect(gpos)
                self.Update_Area(r)
                pygame.draw.rect(output, (120,120,50), r, 1)

            elif (( self.mode == MenuCommand.BUILD_PIPE )
            and ( self.selection is not None )
            and ( isinstance(self.selection, map_items.Node) )):
                # pipe route illustrated

                sp = Grid_To_Scr(self.selection.pos)
                ep = Grid_To_Scr(gpos)
                colour = (80,80,50)

                r = pygame.Rect(sp,(2,2)).union(pygame.Rect(ep,(2,2)))
                self.Update_Area(r)

                pygame.draw.line(output, colour, sp, ep, 2)

        for item in self.net.popups:
            r = item.Draw_Popup(output)
            self.Update_Area(r)

        if ( not paused ):
            self.blink = 0x80 | ( 0xff & ( self.blink + 0x10 ))
            self.steam_effect_frame = (
                self.steam_effect_frame + 1 ) % len(self.steam_effect)

    def Draw_Stats(self, output: SurfaceType, default_stats: List[StatTuple]) -> None:
        if ( self.selection is None ):
            l = default_stats
        else:
            l = self.selection.Get_Information()
            if ( not self.net.Is_Connected(self.selection) ):
                l += [ ((255,0,0), 15, "Not connected to network") ]

        h = hash(str(l))
        if ( h != self.stats_hash ):
            # Stats have changed.
            output.fill((0,0,0))
            stats.Draw_Stats_Window(output, l)
            self.stats_hash = h


    def Draw_Controls(self, output: SurfaceType) -> None:
        if ( self.control_menu is None ):
            self.__Make_Control_Menu(output.get_rect().width)
        assert self.control_menu is not None
        self.control_menu.Draw(output)

    def Control_Mouse_Move(self, spos: SurfacePosition) -> None:
        if ( self.control_menu is not None ):
            self.control_menu.Mouse_Move(spos)

    def Control_Mouse_Down(self, spos: SurfacePosition) -> None:
        if ( self.control_menu is not None ):
            self.control_menu.Mouse_Down(spos)
            self.mode = self.control_menu.Get_Command()

            if ( self.selection is not None ):
                if ( self.mode == MenuCommand.DESTROY ):
                    self.demo.Action("Destroy", self.selection)
                    self.net.Destroy(self.selection)
                    self.__Clear_Control_Selection()
                    self.selection = None
                    self.Update_Game()

                elif ( self.mode == MenuCommand.UPGRADE ):
                    self.demo.Action("Upgrade", self.selection)
                    self.selection.Begin_Upgrade()
                    self.__Clear_Control_Selection()

    def Key_Press(self, k: int) -> None:
        if ( self.control_menu is not None ):
            self.control_menu.Key_Press(k)
            self.mode = self.control_menu.Get_Command()

    def Right_Mouse_Down(self) -> None:
        self.selection = None
        self.mouse_pos = None
        self.__Clear_Control_Selection()

    def Cancel_Fast_Forward(self) -> None:
        if self.mode == MenuCommand.FAST_FORWARD:
            self.__Clear_Control_Selection()

    def __Clear_Control_Selection(self) -> None:
        self.mode = MenuCommand.NEUTRAL
        if ( self.control_menu is not None ):
            self.control_menu.Select(MenuCommand.NEUTRAL)

    def Reset(self) -> None:
        self.selection = None
        self.mouse_pos = None
        self.__Clear_Control_Selection()
        self.stats_hash = 0
        self.__Update_Reset()
        self.Update_Game() # after a reset...

    def __Update_Reset(self) -> None:
        self.full_update = False
        self.partial_update = False
        self.update_area_list = []

    def Is_Menu_Open(self) -> bool:
        return ( self.mode == MenuCommand.OPEN_MENU )

    def Is_Fast_Forward(self) -> bool:
        return ( self.mode == MenuCommand.FAST_FORWARD )

    def Game_Mouse_Down(self, spos: SurfacePosition) -> None:
        gpos = Scr_To_Grid(spos)

        if (( self.selection is not None )
        and ( self.selection.Is_Destroyed() )):
            self.selection = None

        here = self.net.ground_grid.get(gpos, None)
        if here is None:
            # empty grid square (possibly containing pipes)
            self.selection = self.net.Get_Pipe(gpos)

            if ( self.mode == MenuCommand.BUILD_NODE ):
                # create new node!
                n = map_items.Node(gpos)
                n.Sound_Effect()
                self.selection = None
                self.demo.Action("Build_Node", n)
                if self.net.Add_Grid_Item(n):
                    self.selection = n
                    tutor.Notify_Add_Node(n)

            elif ( self.mode == MenuCommand.DESTROY ):
                # I presume you are referring to a pipe?
                pipe = self.selection
                if ( pipe is not None ):
                    self.demo.Action("Destroy", self.selection)
                    self.net.Destroy(pipe)
                    self.__Clear_Control_Selection()
                    self.Update_Game()
                self.selection = None

            elif ( self.mode == MenuCommand.UPGRADE ):
                if ( self.selection is not None ):
                    self.demo.Action("Upgrade", self.selection)
                    self.selection.Begin_Upgrade()
                    self.__Clear_Control_Selection()

            elif ( self.selection is not None ):
                self.selection.Sound_Effect()

        elif isinstance(here, map_items.Node):
            # grid square contains a node

            n = typing.cast(map_items.Node, here)
            if ( self.mode == MenuCommand.BUILD_PIPE ):
                if (( self.selection is None )
                or ( isinstance(self.selection, map_items.Pipe))):
                    # start a new pipe here
                    self.selection = n
                    n.Sound_Effect()

                elif (( isinstance(self.selection, map_items.Node) )
                and ( n != self.selection )):
                    # end pipe here
                    self.demo.Action("Add_Pipe", self.selection, n)
                    if ( self.net.Add_Pipe(self.selection, n) ):
                        tutor.Notify_Add_Pipe()
                        self.selection = None

            elif ( self.mode == MenuCommand.DESTROY ):
                self.demo.Action("Destroy", n)
                self.net.Destroy(n)
                self.selection = None
                self.__Clear_Control_Selection()
                self.Update_Game()

            elif ( self.mode == MenuCommand.UPGRADE ):
                self.demo.Action("Upgrade", n)
                n.Begin_Upgrade()
                self.selection = n
                self.__Clear_Control_Selection()

            else:
                self.selection = n
                n.Sound_Effect()

        else:
            # A non-empty, non-Node grid square must be a well
            assert isinstance(here, map_items.Well)
            if self.mode == MenuCommand.BUILD_NODE:
                # A node is planned on top of the well.
                self.selection = None
                n = map_items.Well_Node(gpos)
                self.demo.Action("Build_Node", n)
                if self.net.Add_Grid_Item(n):
                    self.selection = n
                    self.selection.Sound_Effect()


        if self.selection is None:
            self.demo.Action("Unselect")
        else:
            self.demo.Action("Select", self.selection)
        self.net.Popup(self.selection)
        tutor.Notify_Select(self.selection)

    def Game_Mouse_Move(self, spos: SurfacePosition) -> None:
        self.mouse_pos = Scr_To_Grid(spos)
        if ( self.control_menu is not None ):
            self.control_menu.Mouse_Move(None)

    def Add_Steam_Effect(self, output: SurfaceType, pos: GridPosition) -> None:
        sfx = self.steam_effect[ self.steam_effect_frame ]
        r = sfx.get_rect()
        r.midbottom = Grid_To_Scr(pos)
        output.blit(sfx, r.topleft)
        self.Update_Area(r)

    def __Make_Control_Menu(self, width: int) -> None:
        pictures: Dict[MenuCommand, str] = dict()
        pictures[ MenuCommand.BUILD_NODE ] = "bricks.png"
        pictures[ MenuCommand.BUILD_PIPE ] = "bricks2.png"
        pictures[ MenuCommand.DESTROY ] = "destroy.png"
        pictures[ MenuCommand.UPGRADE ] = "upgrade.png"
        pictures[ MenuCommand.OPEN_MENU ] = "menuicon.png"
        pictures[ MenuCommand.FAST_FORWARD ] = "fastforward.png"

        self.control_menu = menu.Enhanced_Menu([
                (MenuCommand.BUILD_NODE, "Build &Node", [ pygame.K_n ]),
                (MenuCommand.BUILD_PIPE, "Build &Pipe", [ pygame.K_p ]),
                (MenuCommand.DESTROY, "&Destroy", [ pygame.K_d , pygame.K_BACKSPACE ]),
                (MenuCommand.UPGRADE, "&Upgrade", [ pygame.K_u ]),
                (None, None, []),
                (MenuCommand.FAST_FORWARD, "Fast Forward", [ pygame.K_F15 ]),
                (None, None, []),
                (MenuCommand.OPEN_MENU, "Menu", [ pygame.K_ESCAPE ])],
                pictures, width)

    def Frame_Advance(self, frame_time: float) -> None:
        for p in self.net.pipe_list:
            p.Frame_Advance(frame_time)

    def Playback_Action(self, name: str, *payload) -> None:
        self.selection = None
        gpos = None
        objects = []

        for i in range(0, len(payload), 2):
            x = payload[i]
            y = payload[i + 1]
            gpos = (x, y)
            obj = self.net.ground_grid.get(gpos, None)
            if obj is not None:
                objects.append(obj)
            if i == 0:
                self.selection = typing.cast(map_items.Building, obj)
            if i == 2:
                self.selection = None
                for pipe in self.net.pipe_list:
                    if (((pipe.n1 == objects[0]) and (pipe.n2 == objects[1]))
                    or ((pipe.n1 == objects[1]) and (pipe.n2 == objects[0]))):
                        self.selection = pipe
                        break

        if name == "Destroy":
            if not self.selection:  # NO-COV
                raise game_random.PlaybackError(
                        "Destroy must always reference a valid "
                        "selection: got " + repr(payload))
            self.net.Destroy(self.selection)

        elif name == "Upgrade":
            if not self.selection:  # NO-COV
                raise game_random.PlaybackError(
                        "Upgrade must always reference a valid "
                        "selection: got " + repr(payload))
            self.selection.Begin_Upgrade()

        elif name == "Build_Node":
            assert gpos
            if isinstance(self.selection, map_items.Well):
                n1 = map_items.Well_Node(gpos)
                rc = self.net.Add_Grid_Item(n1)
            else:
                assert not self.selection
                n2 = map_items.Node(gpos)
                rc = self.net.Add_Grid_Item(n2)
                if rc:
                    tutor.Notify_Add_Node(n2)

        elif name == "Add_Pipe":
            assert len(payload) >= 4
            assert isinstance(objects[0], map_items.Node)
            assert isinstance(objects[1], map_items.Node)
            if self.net.Add_Pipe(objects[0], objects[1]) is not None:
                tutor.Notify_Add_Pipe()

        elif name == "Select":
            assert self.selection
            self.net.Popup(self.selection)
            tutor.Notify_Select(self.selection)

        else:
            assert name == "Unselect"
            assert not self.selection
            self.net.Popup(self.selection)
            tutor.Notify_Select(self.selection)

        self.selection = None
