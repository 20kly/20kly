# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Do you believe in the users?

import pygame , random
from pygame.locals import *

import stats , menu , draw_obj , mail , particle , tutor
from map_items import *
from primitives import *


class User_Interface:
    def __init__(self, net, (width, height)):
        self.net = net
        self.control_menu = None


        self.Reset()
        self.blink = 0xff

        img = resource.Load_Image("back.jpg").convert() # convert destroys a-channel

        # Although there is only one base image, it is flipped and
        # rotated on startup to create one of eight possible backdrops.
        # (Note: These don't get saved, as they're part of the UI. That's bad.)

        img = pygame.transform.rotate(img, 90 * random.randint(0,3))
        if ( random.randint(0,1) == 0 ):
            img = pygame.transform.flip(img, True, False)
            
        self.background = pygame.transform.scale(img, (width, height))

        self.steam_effect = particle.Make_Particle_Effect(particle.Steam_Particle)
        self.steam_effect_frame = 0


    def Update_Area(self, area):
        if ( area != None ):
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

    def Update_All(self):
        self.full_update = True

    def Draw_Game(self, output, season_fx):
        blink = self.blink

        if ( season_fx.Is_Shaking() and not self.Is_Menu_Open() ):
            # Earthquake effect
            m = 6
            r = output.get_rect()
            r.left += random.randint(-m, m)
            r.top += random.randint(-m, m)
            r = output.get_rect().clip(r)
            output = output.subsurface(r)
            self.Update_All()

        if ( self.net.dirty ):
            self.Update_All()
            self.net.dirty = False

        if ( mail.Has_New_Mail() or tutor.Has_Changed() ):
            self.Update_All() # force update

        # These things may not need to be redrawn
        # as they are never animated and can't be selected.

        if ( self.full_update ):
            output.blit(self.background,(0,0))

            self.__Update_Reset()

            for w in self.net.well_list:
                w.Draw(output)
                self.Add_Steam_Effect(output, w.pos)

        else:
            if ( DEBUG_UPDATES ):
                x = output.get_rect().width
                for y in range(0,output.get_rect().height,2):
                    pygame.draw.line(output, (0,0,0),
                        (0,y), (x,y))
            
            for u in self.update_area_list:
                output.blit(self.background, u.topleft, u)

            self.__Update_Reset()

            for w in self.net.well_list:
                w.Draw(output)
                self.Add_Steam_Effect(output, w.pos)


        # Everything else needs to be redrawn every turn.

        if ( self.selection != None ):
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
        if ( gpos != None ):
            if ( self.mode == BUILD_NODE ):
                # could put a node here.
                r = Grid_To_Scr_Rect(gpos)
                self.Update_Area(r)
                pygame.draw.rect(output, (120,120,50), r, 1)

            elif (( self.mode == BUILD_PIPE )
            and ( self.selection != None )
            and ( isinstance(self.selection, Node) )):
                # pipe route illustrated

                sp = Grid_To_Scr(self.selection.pos)
                ep = Grid_To_Scr(gpos)
                colour = (80,80,50)

                if ( not self.net.Pipe_Possible(self.selection.pos, gpos) ):
                    colour = (100,0,0)

                r = Rect(sp,(2,2)).union(Rect(ep,(2,2)))
                self.Update_Area(r)

                pygame.draw.line(output, colour, sp, ep, 2)
    
        for item in self.net.popups:
            r = item.Draw_Popup(output)
            self.Update_Area(r)

        mail.Draw_Mail(output)

        if ( not self.Is_Menu_Open () ):
            self.blink = 0x80 | ( 0xff & ( self.blink + 0x10 ))
            self.steam_effect_frame = ( 
                self.steam_effect_frame + 1 ) % len(self.steam_effect)

        if ( DEBUG_GRID ):
            self.Debug_Grid(output)

    def Draw_Selection(self, output):
        output.fill((20,0,0))
        if ( self.selection != None ):
            r = output.get_rect()
            r.center = Grid_To_Scr(self.selection.pos)

            for p in self.net.pipe_list:
                p.Draw_Mini(output, r.topleft)

            for n in self.net.node_list:
                n.Draw_Mini(output, r.topleft)

    def Draw_Stats(self, output, default_stats):
        if ( self.selection == None ):
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

        
    def Draw_Controls(self, output):
        if ( self.control_menu == None ):
            self.__Make_Control_Menu(output.get_rect().width)
        self.control_menu.Draw(output)

    def Control_Mouse_Move(self, spos):
        if ( self.control_menu != None ):
            self.control_menu.Mouse_Move(spos)

    def Control_Mouse_Down(self, spos):
        if ( self.control_menu != None ):
            self.control_menu.Mouse_Down(spos)
            self.mode = self.control_menu.Get_Command()

            if ( self.selection != None ):
                if ( self.mode == DESTROY ):
                    self.net.Destroy(self.selection)
                    self.__Clear_Control_Selection()
                    self.selection = None
                    self.Update_All()

                elif ( self.mode == UPGRADE ):
                    self.selection.Begin_Upgrade()
                    self.__Clear_Control_Selection()

    def Key_Press(self, k):
        if ( self.control_menu != None ):
            self.control_menu.Key_Press(k)
            self.mode = self.control_menu.Get_Command()

    def Right_Mouse_Down(self):
        self.selection = None
        self.mouse_pos = None
        self.__Clear_Control_Selection()

    def __Clear_Control_Selection(self):
        self.mode = NEUTRAL
        if ( self.control_menu != None ):
            self.control_menu.Select(NEUTRAL)

    def Reset(self):
        self.selection = None
        self.mouse_pos = None
        self.__Clear_Control_Selection()
        self.stats_hash = 0
        self.__Update_Reset()
        self.Update_All() # after a reset...

    def __Update_Reset(self):
        self.full_update = False
        self.partial_update = False
        self.update_area_list = []

    def Is_Menu_Open(self):
        return ( self.mode == OPEN_MENU )

    def Game_Mouse_Down(self, spos):
        gpos = Scr_To_Grid(spos)

        if (( self.selection != None )
        and ( self.selection.Is_Destroyed() )):
            self.selection = None

        if ( DEBUG ):
            print 'Selection:',self.selection
            for (i,n) in enumerate(self.net.node_list):
                if ( n == self.selection ):
                    print 'Found: node',i
            for (i,p) in enumerate(self.net.pipe_list):
                if ( p == self.selection ):
                    print 'Found: pipe',i
            print 'End'


        if ( not self.net.ground_grid.has_key(gpos) ):
            self.selection = self.net.Get_Pipe(gpos)

            # empty (may contain pipes)
            if ( self.mode == BUILD_NODE ):
                # create new node!
                n = Node(gpos)
                n.Sound_Effect()
                self.selection = None
                if ( self.net.Add_Grid_Item(n) ):
                    self.selection = n
                    tutor.Notify_Add_Node(n)

            elif ( self.mode == DESTROY ):
                # I presume you are referring to a pipe?
                pipe = self.selection
                if ( pipe != None ):
                    self.net.Destroy(pipe)
                    self.__Clear_Control_Selection()
                    self.Update_All()
                self.selection = None

            elif ( self.mode == UPGRADE ):
                if ( self.selection != None ):

                    self.selection.Begin_Upgrade()
                    self.__Clear_Control_Selection()

            elif ( self.selection != None ):
                self.selection.Sound_Effect()
                
        elif ( isinstance(self.net.ground_grid[ gpos ], Node)):
            # Contains node

            n = self.net.ground_grid[ gpos ]
            if ( self.mode == BUILD_PIPE ):
                if (( self.selection == None )
                or ( isinstance(self.selection, Pipe))):
                    # start a new pipe here
                    self.selection = n
                    n.Sound_Effect()

                elif (( isinstance(n, Node) )
                and ( isinstance(self.selection, Node) )
                and ( n != self.selection )):
                    # end pipe here
                    if ( self.net.Add_Pipe(self.selection, n) ):
                        tutor.Notify_Add_Pipe()
                        self.selection = None

            elif ( self.mode == DESTROY ):
                self.net.Destroy(n)
                self.selection = None
                self.__Clear_Control_Selection()
                self.Update_All()

            elif ( self.mode == UPGRADE ):
                n.Begin_Upgrade()
                self.selection = n
                self.__Clear_Control_Selection()

            else:
                self.selection = n
                n.Sound_Effect()

        elif ( isinstance(self.net.ground_grid[ gpos ], Well)):
            # Contains well (unimproved)
            w = self.net.ground_grid[ gpos ]
            if ( self.mode == BUILD_NODE ):
                # A node is planned on top of the well.
                self.selection = None
                n = Well_Node(gpos)
                if ( self.net.Add_Grid_Item(n) ):
                    self.selection = n
                    self.selection.Sound_Effect()


        self.net.Popup(self.selection)
        tutor.Notify_Select(self.selection)

    def Game_Mouse_Move(self, spos):
        self.mouse_pos = Scr_To_Grid(spos)
        if ( self.control_menu != None ):
            self.control_menu.Mouse_Move(None)

    def Debug_Grid(self, output):
        (mx, my) = GRID_SIZE
        for y in xrange(my):
            for x in xrange(mx):
                if ( self.net.pipe_grid.has_key( (x,y) ) ):
                    r = Grid_To_Scr_Rect((x,y))
                    pygame.draw.rect(output, (55,55,55), r, 1)
                    r.width = len(self.net.pipe_grid[ (x,y) ]) + 1
                    pygame.draw.rect(output, (255,0,0), r)

    def Add_Steam_Effect(self, output, pos):
        sfx = self.steam_effect[ self.steam_effect_frame ]
        r = sfx.get_rect()
        r.midbottom = Grid_To_Scr(pos)
        output.blit(sfx, r.topleft)
        self.Update_Area(r)

    def __Make_Control_Menu(self, width):
        pictures = dict()
        pictures[ BUILD_NODE ] = "bricks.png"
        pictures[ BUILD_PIPE ] = "bricks2.png"
        pictures[ DESTROY ] = "destroy.png"
        pictures[ UPGRADE ] = "upgrade.png"
        pictures[ OPEN_MENU ] = "menuicon.png"

        self.control_menu = menu.Enhanced_Menu([
                (BUILD_NODE, "Build &Node", [ K_n ]),
                (BUILD_PIPE, "Build &Pipe", [ K_p ]),
                (DESTROY, "&Destroy", [ K_d , K_BACKSPACE ]),
                (UPGRADE, "&Upgrade", [ K_u ]),
                (None, None, None),
                (OPEN_MENU, "Menu", [ K_ESCAPE ])], 
                pictures, width)

    def Frame_Advance(self, frame_time):
        for p in self.net.pipe_list:
            p.Frame_Advance(frame_time)


