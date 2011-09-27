# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 
#
# The main loop of the game. This procedure is running
# whenever the game is on the screen.

import pygame, sys, time, pickle, random
from pygame.locals import *

import bresenham , intersect , extra , stats , mail , screen
import menu , startup , save_menu , save_game , config , resource
import review , sound , tutor
from primitives import *
from colours import *
from quiet_season import Quiet_Season
#from alien_invasion import Alien_Season
#from quakes import Quake_Season
#from storms import Storm_Season
from map_items import *
from steam_model import FRAME_RATE
from net_model import Network
from ui import User_Interface
from mail import New_Mail

BUTTON_LEFT = 1

game = None

class Game_Data:
    pass

def Create_Game(challenge):
    # Make game data holder
    global game
    game = Game_Data()

    teaching = ( challenge == MENU_TUTORIAL )

    game.version = startup.Get_Game_Version()
    game.sysinfo = extra.Get_System_Info()

    # Steam network initialisation
    game.net = Network(teaching, random.randrange(0, 1 << 32))

    DIFFICULTY.Set(MENU_INTERMEDIATE)

    # Establish equilibrium with initial network.
    for i in xrange(100):
        game.net.Compute()

    # Game variables
    game.season = SEASON_START
    game.season_ends = 0
    game.season_effect = 0
    game.season_fx = Quiet_Season(game.net)
    game.work_units_used = 0 
    game.challenge = challenge
    game.game_ends_at = None
    game.game_running = True
    game.game_time = 0
    game.win = False
    game.warning_given = False
    game.wu_integral = 0
    game.bg_number = random.randrange(0, 1 << 32)

def Main_Loop(restore_pos):
    global game

    # Initialisation of screen things.
    (width, height) = screen.Update_Resolution()
    menu_margin = height
    screen.surface.fill(BLACK)
    pygame.display.flip()
    tutor.Off() 

    draw_obj.Flush_Draw_Obj_Cache() # in case of resize
    
    # Grid setup
    (w,h) = GRID_SIZE
    assert w == h
    Set_Grid_Size(height / h)

    # Right-hand side windows are removed 
    game_screen_rect = Rect(SCROLL_MARGIN, SCROLL_MARGIN, 
                    width - (SCROLL_MARGIN * 2),
                    height - (SCROLL_MARGIN * 2))
    game_screen_surf = screen.surface.subsurface(game_screen_rect)

    menu_button_rect = Rect(0, 0, SCROLL_MARGIN * 3, SCROLL_MARGIN * 3)
    
    alarm_sound = sound.Persisting_Sound("emergency")

    # UI setup
    ui = User_Interface(game.net, (width, height), game.bg_number)

    exit_options = [
        (MENU_MENU, "Exit to Main Menu", []),
        (MENU_QUIT, "Exit to " + extra.Get_OS(), [ K_F10 ])]

    save_available = [(MENU_SAVE, "Save Game", []),
        (MENU_LOAD, "Restore Game", []),
        (None, None, [])]

    if ( game.challenge == MENU_TUTORIAL ):
        save_available = []

    in_game_menu = menu.Menu([
        (None, None, []),
        (MENU_MUTE, "Toggle Sound", []),
        (None, None, []) ] +
        save_available + [
        (MENU_HIDE, "Return to Game", [ K_ESCAPE ])] + exit_options)

    current_menu = in_game_menu

    flash = True
    quit_state = MENU_LOOP_RUN
    in_game_menu.Select(None)
    mail.Initialise()
    autosave_timer = 0

    DIFFICULTY.Set(game.challenge)
    

    def Summary():
        lev = dict()
        lev[ MENU_TUTORIAL ] = "a Tutorial"
        lev[ MENU_BEGINNER ] = "a Beginner"
        lev[ MENU_INTERMEDIATE ] = "an Intermediate"
        lev[ MENU_EXPERT ] = "an Expert"
    
        assert game.challenge != None
        assert lev.has_key( game.challenge )
        New_Mail("You are playing " + lev[ game.challenge ] + " game.")

    # Almost ready to start... but are we starting
    # from a savegame?
    def Restore(cmd):
        global game
        (g2, result) = save_game.Load(game, cmd)
        if ( result == None ):
            game = g2
            ui.net = game.net
            mail.Initialise()
            assert game.challenge != None
            DIFFICULTY.Set(game.challenge)
            New_Mail("Game restored. It is the " + 
                game.season_fx.name + " season.")
        else:
            New_Mail(result)
    
    if ( restore_pos != None ):
        game.challenge = MENU_INTERMEDIATE
        Restore(restore_pos)

    assert game.challenge != None
    Summary()

    if ( game.challenge == MENU_TUTORIAL ):
        tutor.On(( menu_margin * 40 ) / 100)

    # In Game - Main loop
    while ( quit_state == MENU_LOOP_RUN ):

        if ( game.game_running ):
            flash = not flash

        draw_obj.Next_Frame() # Flashing lights on the various items
        ui.Draw_Game(game_screen_surf, game.season_fx)
        pygame.draw.rect(screen.surface, CYAN, menu_button_rect)

        game.season_fx.Per_Frame(1)
        ui.Frame_Advance()
        game.net.Compute()

        pygame.display.flip()
        screen.clock.tick(FRAME_RATE)

        # Events
        e = screen.Get_Event(False)
        while ( e.type != NOEVENT ):
            if e.type == QUIT:
                quit_state = MENU_QUIT
                break

            elif e.type == VIDEORESIZE:
                quit_state = MENU_RESIZE_EVENT

            elif ((e.type == MOUSEBUTTONDOWN)
            and (e.button == BUTTON_LEFT)):
                # Left mouse down
                (x, y) = e.pos
                if menu_button_rect.collidepoint(e.pos):
                    # on menu button
                    quit_state = MENU_MENU
                    
                elif game_screen_rect.collidepoint(e.pos):
                    # on game window
                    ui.Game_Mouse_Down(
                            (x - game_screen_rect.left,
                            y - game_screen_rect.top))
                
                else:
                    # on scrollbar 
                    pass

            elif (e.type == MOUSEMOTION):
                (x, y) = e.pos
                ui.Game_Mouse_Move(
                            (x - game_screen_rect.left,
                            y - game_screen_rect.top))

            elif ((e.type == MOUSEBUTTONUP)
            and (e.button == BUTTON_LEFT)):
                (x, y) = e.pos
                ui.Game_Mouse_Up((
                        x - game_screen_rect.left,
                        y - game_screen_rect.top))
                
            elif e.type == KEYDOWN:
                ui.Key_Press(e.key)

            elif ((e.type == MOUSEBUTTONDOWN)
            and (e.button != BUTTON_LEFT)):
                ui.Right_Mouse_Down()

            e = screen.Get_Event(False)


    tutor.Off()
    alarm_sound.Set(0.0)

    if quit_state != MENU_MENU:
        return quit_state

    # In Game - Menu
    quit_state = MENU_LOOP_RUN
    while quit_state == MENU_LOOP_RUN:
        current_menu.Draw(screen.surface)
       
        pygame.display.flip()
        screen.clock.tick(FRAME_RATE)

        # Events
        e = screen.Get_Event(True)
        while ( e.type != NOEVENT ):
            if e.type == QUIT:
                quit_state = MENU_QUIT
                break

            elif e.type == VIDEORESIZE:
                quit_state = MENU_RESIZE_EVENT

            elif ((e.type == MOUSEBUTTONDOWN)
            and (e.button == BUTTON_LEFT)):
                current_menu.Mouse_Down(e.pos)

            elif e.type == MOUSEMOTION:
                current_menu.Mouse_Move(e.pos)

            elif e.type == KEYDOWN:
                current_menu.Key_Press(e.key)

            e = screen.Get_Event(False)

        cmd = current_menu.Get_Command()
        current_menu.Select(None) # consume command

        if ( current_menu == in_game_menu ):

            # It's the normal menu.
            if ( cmd == MENU_QUIT ):
                quit_state = MENU_QUIT
                ui.Reset() # makes menu disappear

            elif ( cmd == MENU_MENU ):
                quit_state = MENU_MENU
                ui.Reset()

            elif ( cmd == MENU_SAVE ):
                if ( game.game_running ):
                    # Switch to alternate menu
                    current_menu = save_menu.Save_Menu(True)

            elif ( cmd == MENU_LOAD ):
                current_menu = save_menu.Save_Menu(False)

            elif ( cmd == MENU_REVIEW ):
                quit_state = MENU_REVIEW
                ui.Reset()

            elif ( cmd != None ):
                # Default option - back to game
                if ( not game.game_running ):
                    New_Mail("Sorry - the game has finished")
                ui.Reset() 

        else:
            # It's another menu! That means it's the save menu.
            if (( cmd != None )
            and ( cmd >= 0 )):
                if ( not current_menu.Is_Saving() ):
                    Restore(cmd)

                else:
                    label = "%s season - %s" % (
                            game.season_fx.name, time.asctime())

                    game.net.Make_Ready_For_Save()
                    result = save_game.Save(game, cmd, label)
                    if ( result == None ):
                        New_Mail("Game saved.")
                    else:
                        New_Mail(result)

            if ( cmd != None ):
                # Back to game.
                Special_Refresh()
                current_menu = in_game_menu
                ui.Reset()

    return quit_state


