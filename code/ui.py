# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Do you believe in the users?

import pygame 
from pygame.locals import *

import stats , menu , draw_obj , mail , particle , tutor
from map_items import *
from primitives import *
from colours import *

[ STATE_MOUSE_UP, STATE_MOUSE_DOWN, STATE_POPUP_MENU ] = "xyz"

class User_Interface:
    """User interface provides both the view of the game
    and the means to interact with it."""
    def __init__(self, net, (width, height), bg_number):
        """The user interface will be recreated whenever the
        window is resized. It is not part of a saved game."""
        self.net = net

        self.Reset()
        self.blink = 0xff

        self.screen_rect = Rect(0, 0, width, height)

        img = resource.Load_Image("back.jpg").convert() 
        # (convert destroys a-channel)
        # Although there is only one base image, it is flipped and
        # rotated on startup to create one of eight possible backdrops.

        img = pygame.transform.rotate(img, 90 * (bg_number & 3))
        if bg_number & 4:
            img = pygame.transform.flip(img, True, False)
            
        self.background = pygame.transform.scale(img, (width, height))

        self.steam_effect = particle.Make_Particle_Effect(
                        particle.Steam_Particle)
        self.steam_effect_frame = 0

    # PUBLIC. Top-level drawing function.
    def Draw_Game(self, output, season_fx):
        """Top-level drawing function; game is drawn on the output surface."""

        blink = self.blink

        if season_fx.Is_Shaking():
            # Earthquake effect
            m = 6
            r = output.get_rect()
            r.left += self.net.random(2 * m) - m
            r.top += self.net.random(2 * m) - m
            r = output.get_rect().clip(r)
            output = output.subsurface(r)

        # Drawing with painters algorithm
        output.blit(self.background,(0,0))

        # Wells
        for w in self.net.well_list:
            w.Draw(output)
            self.Draw_Steam_Effect(output, w.pos)

        # Selection layers
        if ((self.mouse_over_selection != None)
        and (self.mouse_over_selection != self.selection)):
            x = blink / 2
            self.mouse_over_selection.Draw_Selected(output, (x, x, x))

        if self.selection != None:
            self.selection.Draw_Selected(output, (blink, blink, 0))

        # Work units
        for unit in self.net.work_queue:
            unit.Draw(output)

        # Pipes
        for p in self.net.pipe_list:
            p.Draw(output)

        # Nodes
        for n in self.net.node_list:
            n.Draw(output)
            if n.emits_steam:
                self.Draw_Steam_Effect(output, n.pos)

        # Seasons
        def Ignore(rect): pass
        season_fx.Draw(output, Ignore)
    
        # Whatever the user is currently doing
        if self.do_drawing != None:
            self.do_drawing(output)

        # Mail messages
        mail.Draw_Mail(output)

        self.blink = 0x80 | ( 0xff & ( self.blink + 0x10 ))
        self.steam_effect_frame = ( 
            self.steam_effect_frame + 1 ) % len(self.steam_effect)

        # Debugging 
        if DEBUG_GRID:
            self.Draw_Debug_Grid(output)

        # This concludes drawing

    # PUBLIC. 
    def Frame_Advance(self):
        """Advance the game animations."""
        for p in self.net.pipe_list:
            p.Frame_Advance()

    def Reset(self):
        """Reset status of selection."""
        self.selection = self.target = None
        self.mouse_over_selection = None
        self.state = STATE_MOUSE_UP
        self.selection_spos = self.target_spos = (-100, -100)
        self.popup_menu = None
        self.do_drawing = None

    # PRIVATE. Search operations.
    def Get_Item(self, gpos, commit):
        """Identify the item at the given grid position. May be a Well,
        a Well_Node, a Pipe, a City_Node, a Node, or None. If commit == True
        then this may reorder the items at that location."""

        node = self.net.ground_grid.get(gpos, None)
        if node != None:
            return node

        return self.net.Get_Pipe(gpos, commit)

    def Get_Popup_Menu(self):
        """Obtain the contents of the popup menu for the current
        selection. This will be a newui.Popup_Menu object or None."""

        if self.selection == None:
            return None

        return self.selection.Get_Popup_Menu()

    # PUBLIC. Action functions, executed on a mouse event.
    def Game_Mouse_Down(self, spos):
        """Mouse button down at given screen position."""

        if ((self.state == STATE_POPUP_MENU)
        and (self.popup_menu.rect.collidepoint(spos))):
            # Click on popup menu
            self.Game_Mouse_Activity(spos, True)
        else:
            self.target = self.selection = None
            self.selection_spos = spos

            gpos = Scr_To_Grid(spos)
            self.state = STATE_MOUSE_DOWN
            self.selection = self.Get_Item(gpos, True)
            tutor.Notify_Select(self.selection)
            self.Game_Mouse_Activity(spos, False)

            if self.selection != None:
                self.selection.Debug()

    def Game_Mouse_Move(self, spos):
        """Mouse motion to given screen position."""
        self.Game_Mouse_Activity(spos, False)

    def Game_Mouse_Up(self, spos):
        """Mouse button up at given screen position."""
        self.Game_Mouse_Activity(spos, True)

    def Right_Mouse_Down(self):
        """Right mouse button events are used as a universal
        'cancel' command. RMB resets the selection state."""

        self.Reset()

    # PUBLIC. Action function for key event
    def Key_Press(self, k):
        """Register key press."""
        if k == K_ESCAPE:
            if self.selection != None:
                self.Reset()
            else:
                # Open menu
                pass

    # PRIVATE. Mouse activity handlers
    def Game_Mouse_Activity(self, spos, commit):
        """Register some mouse activity at the given screen position.
        If commit == False then the activity is merely illustrated
        on screen. If commit == True then the activity is made final."""

        gpos = Scr_To_Grid(spos)
        self.target_spos = spos
        self.do_drawing = None

        pointing_at = self.Get_Item(gpos, False)
        self.mouse_over_selection = pointing_at

        if self.state == STATE_POPUP_MENU:
            # Popup menu on screen
            self.do_drawing = self.popup_menu.Draw

        if ((self.state == STATE_MOUSE_DOWN)
        and (self.selection != None)
        and (isinstance(self.selection, Node))):
            # Mouse clicked on a node
            self.target = pointing_at

            if self.target == self.selection:
                # Mouse on initial node
                if commit:
                    self.Popup_Menu_Appears(spos)

            elif ((self.target != None)
            and isinstance(self.target, Well)):
                # Mouse clicked on a well
                self.do_drawing = self.Draw_New_Pipe_And_New_Well
                if commit:
                    self.Create_Activity(Well_Node, gpos, 
                            [self.selection, self.target])

            elif ((self.target != None)
            and isinstance(self.target, Node)):
                # Mouse on another existing node
                self.do_drawing = self.Draw_New_Pipe
                if commit:
                    if self.net.Add_Pipe(self.selection, self.target):
                        tutor.Notify_Add_Pipe()

                    self.selection = None

            elif ((self.target != None)
            and isinstance(self.target, Pipe)):
                # Mouse on an existing pipe, try to create joint
                self.do_drawing = self.Draw_New_Pipe_And_New_Node
                is_possible = self.net.Is_Pipe_Possible(   
                                Scr_To_Grid(self.selection_spos), gpos, 
                                [self.selection], True)

                if commit:
                    if is_possible:
                        n = Node(gpos)
                        if self.net.Add_Node_Pipe_Split(n):
                            tutor.Notify_Add_Node(n)
                            if self.net.Add_Pipe(self.selection, n):
                                tutor.Notify_Add_Pipe()

                    self.selection = None

                elif not is_possible:
                    # Invalid target here
                    self.do_drawing = self.Draw_New_Pipe
                    self.target = None

            else:
                # Mouse in free space, try to create node
                self.do_drawing = self.Draw_New_Pipe_And_New_Node
                if commit:
                    self.Create_Activity(Node, gpos, [self.selection])

        elif ((self.state == STATE_MOUSE_DOWN)
        and (self.selection != None)
        and (isinstance(self.selection, Pipe))):
            # Mouse clicked on a pipe

            if pointing_at == self.selection:
                # Pipe selected
                if commit:
                    self.Popup_Menu_Appears(spos)

        elif ((self.state == STATE_POPUP_MENU)
        and (self.popup_menu.rect.collidepoint(spos))):
            # Mouse over popup menu
            self.Popup_Mouse_Activity(spos, commit)

        elif ((self.state == STATE_MOUSE_DOWN)
        and (self.selection == None)):
            # Mouse over free space; nothing selected
            # Javascript-style map scrolling
            (x1, y1) = spos
            (x2, y2) = self.selection_spos

            # scrolling here

        if commit and (self.state == STATE_MOUSE_DOWN):
            self.state = STATE_MOUSE_UP


    def Create_Activity(self, node_class, gpos, allowed):
        """Create a Node at the specified grid position using
        the specified class. A Pipe is also created from the
        initial selection."""

        if self.net.Is_Pipe_Possible(gpos, 
                    Scr_To_Grid(self.selection_spos),
                    allowed, False):

            n = node_class(gpos)
            if self.net.Add_Grid_Item(n):
                tutor.Notify_Add_Node(n)

                if self.net.Add_Pipe(self.selection, n):
                    tutor.Notify_Add_Pipe()

        self.selection = None

    def Popup_Mouse_Activity(self, spos, commit):
        """Mouse activity for a popup menu.
        If commit == False then the activity is merely illustrated
        on screen. If commit == True then the activity is made final."""
    
        kill = True
        if (self.selection != None) and (self.popup_menu != None):
            # popup menu has valid state
            self.popup_menu.Mouse_Move(spos)

            if commit:
                self.popup_menu.Mouse_Down()

            else:
                kill = False

        if kill:
            self.state = STATE_MOUSE_UP
            self.popup_menu = None
            self.selection = None

    # PRIVATE. Unclassified (internal) drawing functions
    def Draw_Debug_Grid(self, output):
        (mx, my) = GRID_SIZE
        for y in xrange(my):
            for x in xrange(mx):
                if ( self.net.pipe_grid.has_key( (x,y) ) ):
                    r = Grid_To_Scr_Rect((x,y))
                    pygame.draw.rect(output, DARK_GREY, r, 1)
                    r.width = len(self.net.pipe_grid[ (x,y) ]) + 1
                    pygame.draw.rect(output, RED, r)

    def Draw_Steam_Effect(self, output, pos):
        sfx = self.steam_effect[ self.steam_effect_frame ]
        r = sfx.get_rect()
        r.midbottom = Grid_To_Scr(pos)
        output.blit(sfx, r.topleft)

    # PRIVATE. Drawing functions that are used when state != STATE_MOUSE_UP
    def Draw_New_Pipe(self, output):
        gpos1 = Scr_To_Grid(self.selection_spos)
        gpos2 = Scr_To_Grid(self.target_spos)
        r1 = Grid_To_Scr_Rect(gpos1)
        r2 = Grid_To_Scr_Rect(gpos2)

        allowed = [self.selection]

        if ((self.target != None)
        and isinstance(self.target, Well)):
            allowed.append(self.target)
            

        colour = VALID_PIPE
        if not self.net.Is_Pipe_Possible(gpos1, gpos2, allowed, True):
            colour = INVALID_PIPE

        pygame.draw.line(output, colour, r1.center, r2.center, 2)

    def Draw_New_Pipe_And_New_Node(self, output):
        self.Draw_New_Pipe(output)

        gpos = Scr_To_Grid(self.target_spos)
        r = Grid_To_Scr_Rect(gpos)
        pygame.draw.rect(output, HIGHLIGHT_GRID, r, 2)

    def Draw_New_Pipe_And_New_Well(self, output):
        self.Draw_New_Pipe(output)

        gpos = Scr_To_Grid(self.target_spos)
        r = Grid_To_Scr_Rect(gpos)
        pygame.draw.rect(output, HIGHLIGHT_GRID, r, 2)

    def Popup_Menu_Appears(self, spos):
        """Setup for popup menu (whenever it appears)."""
        # State change
        self.popup_menu = self.selection.Get_Popup_Menu(self.net)
        self.do_drawing = None

        if self.popup_menu == None:
            # No popup menu available
            return None

        # Decide on location and setup drawing
        self.popup_menu.Place_Menu(spos, self)
        self.state = STATE_POPUP_MENU
        self.do_drawing = self.popup_menu.Draw


