# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 


import pygame , random , sys , math , time , webbrowser , urllib , os
from pygame.locals import *

import game , stats , storms , extra , save_menu , resource , menu
import config , startup , sound , alien_invasion , quakes
from primitives import *


def Main(data_dir):

    n = "20,000 Light-Years Into Space"
    print ""
    print n
    print "Copyright (C) Jack Whitham 2006-07"
    print "Version",startup.Get_Game_Version()
    print ""

    resource.DATA_DIR = data_dir

    config.Initialise()

    # Pygame things
    default_flags = 0
    flags = default_flags
    if ( config.cfg.fullscreen
    and ( not "--window" in sys.argv )):
        flags |= FULLSCREEN

    bufsize = 2048

    no_sound = ( "--no-sound" in sys.argv )
    if ( not no_sound ):
        pygame.mixer.pre_init(22050,-16,2,bufsize)

    pygame.init()
    pygame.font.init()

    if ( no_sound ):
        resource.No_Sound()
    else:
        pygame.mixer.init(22050,-16,2,bufsize)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(config.cfg.resolution, flags)
    height = screen.get_rect().height
    width = screen.get_rect().width

    # Icon
    pygame.display.set_icon(resource.Load_Image("32.png"))


    # Game begins.. show loading image
    screen.fill((0,0,0))
    pygame.display.flip()
    pygame.display.set_caption(n)
    storms.Init_Storms()
    alien_invasion.Init_Aliens()
    quakes.Init_Quakes()

    quit = False
    while ( not quit ):
        if ( config.cfg.resolution != (width, height) ):

            flags = default_flags
            if ( config.cfg.fullscreen ):
                flags |= FULLSCREEN

            # As the toggle mode thing doesn't work outside of Unix, 
            # the fallback strategy is to do set_mode again.
            # But if you set the same mode, then nothing happens.
            # So:
            screen = pygame.display.set_mode((640,480), flags)  # not the right mode
            screen = pygame.display.set_mode(config.cfg.resolution, flags) # right mode!
            height = screen.get_rect().height
            width = screen.get_rect().width

        quit = Main_Menu_Loop(n, clock, screen, (width, height))

    config.Save()

    # Bye bye Pygame.
    pygame.mixer.quit()
    pygame.quit()


def Main_Menu_Loop(name, clock, screen, (width, height)):
    # Further initialisation
    menu_image = resource.Load_Image("mainmenu.jpg")

    if ( menu_image.get_rect().width != width ):
        menu_image = pygame.transform.scale(menu_image, (width, height))

    stats.Set_Font_Scale(config.cfg.font_scale)

    fs = "Fullscreen"
    if ( config.cfg.fullscreen ):
        fs = "Windowed"

    main_menu = current_menu = menu.Menu([ 
                (None, None, []),
                (MENU_TUTORIAL, "Play Tutorial", []),
                (MENU_NEW_GAME, "Play New Game", []),
                (MENU_LOAD, "Restore Game", []),
                (None, None, []),
                (MENU_RES, "Set Graphics Resolution", []),
                (MENU_FULLSCREEN, fs + " Mode", []),
                (MENU_MANUAL, "View Manual", []),
                (None, None, []),
                (MENU_QUIT, "Exit to " + extra.Get_OS(), 
                    [ K_ESCAPE , K_F10 ])])
    resolution_menu = menu.Menu( 
                [(None, None, [])] + [
                (w, "%u x %u Mode" % (w,h), [])
                    for (w, h, fs) in RESOLUTIONS ] +
                [(None, None, []),
                (-1, "Cancel", [])])
    difficulty_menu = menu.Menu( 
                [(None, None, []),
                (MENU_TUTORIAL, "Tutorial", []),
                (None, None, []),
                (MENU_BEGINNER, "Beginner", []),
                (MENU_INTERMEDIATE, "Intermediate", []),
                (MENU_EXPERT, "Expert", []),
                (None, None, []),
                (-1, "Cancel", [])])
    updates_menu = menu.Menu(
                [(None, None, []),
                (MENU_WEBSITE, "Visit Website", []),
                (MENU_UPDATES, "Check for Updates", []),
                (-1, "Cancel", [])])

    copyright = [ name,
            "Copyright (C) Jack Whitham 2006-07 - website: www.jwhitham.org.uk",
            "Special thanks to Acidd_UK for many key improvements.",
            None,
            "Game version " + startup.Get_Game_Version() ]

    if ( screen.get_rect().height > 700 ):
        copyright += [
            "Thanks to andrew_j_w, Jillyanthrax, newsbot3, "
            "nmitchell, and the pyweek organisers." ]

    # off we go.

    quit = False
    while ( not quit ):
        # Main menu
        screen.fill((0,0,0))
        screen.blit(menu_image, (0,0))
      
        y = 5
        sz = 11
        for text in copyright:
            if ( text == None ):
                sz = 7
                continue
            img = stats.Get_Font(sz).render(text, True, (200, 200, 128))
            img_r = img.get_rect()
            img_r.center = (( width * 3 ) / 4, 0)
            img_r.clamp_ip(screen.get_rect())
            img_r.top = y
            screen.blit(img, img_r.topleft)
            y += img_r.height
       
        (quit, cmd) = extra.Simple_Menu_Loop(screen, current_menu,
                (( width * 3 ) / 4, 10 + ( height / 2 )))

        if ( current_menu == main_menu ):
            if ( cmd == MENU_NEW_GAME ):
                current_menu = difficulty_menu
            elif ( cmd == MENU_TUTORIAL ):
                quit = game.Main_Loop(screen, clock, 
                        (width,height), None, MENU_TUTORIAL)
            elif ( cmd == MENU_LOAD ):
                current_menu = save_menu.Save_Menu(False)
            elif ( cmd == MENU_QUIT ):
                quit = True
            elif ( cmd == MENU_FULLSCREEN ):
                config.cfg.fullscreen = not config.cfg.fullscreen

                # This only works in Unix:
                pygame.display.toggle_fullscreen()

                return False # set mode

            elif ( cmd == MENU_RES ):
                current_menu = resolution_menu

            elif ( cmd == MENU_UPDATES ):
                current_menu = updates_menu

            elif ( cmd == MENU_MANUAL ):
                pygame.display.iconify()
                url = os.path.abspath(os.path.join(resource.DATA_DIR, '..',
                            'manual', 'index.html'))
                url = 'file://' + url

                try:
                    webbrowser.open(url, True, True)
                except:
                    pass
                
                
        elif ( cmd != None ):
            if ( current_menu == resolution_menu ):
                for (w, h, fs) in RESOLUTIONS:
                    if ( w == cmd ):
                        config.cfg.resolution = (w, h)
                        config.cfg.font_scale = fs
                        # change res - don't quit
                        return False

            elif ( current_menu == difficulty_menu ):
                if ( cmd >= 0 ):
                    quit = game.Main_Loop(screen, clock, 
                            (width,height), None, cmd)

            elif ( current_menu == updates_menu ):
                website = False

                if ( cmd == MENU_UPDATES ):
                    website = Update_Feature(screen, menu_image)

                elif ( cmd == MENU_WEBSITE ):
                    website = True

                if ( website ):
                    url = ( CGISCRIPT + "v=" +
                            startup.Get_Game_Version() )

                    pygame.display.iconify()
                    try:
                        webbrowser.open(url, True, True)
                    except:
                        pass
                
            else: # Load menu
                if ( cmd >= 0 ):
                    # Start game from saved position
                    quit = game.Main_Loop(screen, clock, 
                            (width,height), cmd, None)

            current_menu = main_menu 

    return True

def Update_Feature(screen, menu_image):
    def Message(msg_list):
        screen.blit(menu_image, (0,0))

        y = screen.get_rect().centery
        for msg in msg_list:
            img_1 = stats.Get_Font(24).render(msg, True, (255, 255, 255))
            img_2 = stats.Get_Font(24).render(msg, True, (0, 0, 0))
            img_r = img_1.get_rect()
            img_r.centerx = screen.get_rect().centerx
            img_r.centery = y
            screen.blit(img_2, img_r.topleft)
            screen.blit(img_1, img_r.move(2,-2).topleft)
            y += img_r.height
        pygame.display.flip()

    def Finish(cerror=None):
        if ( cerror != None ):
            Message(["Connection error:", cerror])

        ok = True
        timer = 4000
        while (( ok ) and ( timer > 0 )):
            e = pygame.event.poll()
            while ( e.type != NOEVENT ):
                if (( e.type == MOUSEBUTTONDOWN )
                or ( e.type == KEYDOWN )
                or ( e.type == QUIT )):
                    ok = False
                e = pygame.event.poll()

            pygame.time.wait( 40 )
            timer -= 40
   
    Message(["Connecting to Website..."])
    url = ( CGISCRIPT + "a=1" )
    new_version = None
    try:
        f = urllib.urlopen(url)
        new_version = f.readline()
        f.close()
    except Exception, x:
        Finish(str(x))
        return False

    if (( new_version == None )
    or ( type(new_version) != str )
    or ( len(new_version) < 2 )
    or ( len(new_version) > 10 )
    or ( not new_version[ 0 ].isdigit() )
    or ( new_version.find('.') <= 0 )):
        Finish("Version data not found.")
        return False

    new_version = new_version.strip()

    # Protect user from possible malicious tampering
    # via a man-in-the-middle attack. I don't want to 
    # render an unfiltered string.
    for i in new_version:
        if (( i != '.' )
        and ( i != '-' )
        and ( not i.isdigit() )
        and ( not i.isalpha() )):
            Finish("Version data is incorrect.")
            return False

    if ( new_version == startup.Get_Game_Version() ):
        Message(["Your software is up to date!",
            "Thankyou for using the update feature."])
        Finish(None)
        return False

    Message(["New version " + new_version + " is available!",
            "Opening website..."])
    Finish(None)
    return True





