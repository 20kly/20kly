# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 


import pygame , sys , math , time , webbrowser , urllib , os
import getopt
from pygame.locals import *

import game , stats , storms , extra , save_menu , resource , menu
import config , startup , sound , alien_invasion , quakes
from primitives import *
from game_random import PlaybackEOF
import primitives

DEB_ICON = '/usr/share/pixmaps/lightyears.xpm'
DEB_MANUAL = '/usr/share/doc/lightyears/html/index.html'
                

def Main(data_dir):

    n = "20,000 Light-Years Into Space"
    print("")
    print(n)
    print("Copyright (C) Jack Whitham 2006-11")
    print("Version", config.CFG_VERSION)
    print("")
    sys.stdout.flush()

    resource.DATA_DIR = data_dir
    
    (opts_list, args) = getopt.getopt(
            sys.argv[1:], "",
            ["safe", "fullscreen",
                "no-sound", "playback=", "record=",
                "resolution=", "challenge="])
    opts = dict(opts_list)
    sys.stdout.flush()

    config.Initialise("--safe" in opts)

    # Pygame things
    flags = 0
    if ("--fullscreen" in opts):
        flags |= FULLSCREEN

    bufsize = 2048

    no_sound = ( "--no-sound" in opts)
    if not no_sound:
        try:
            pygame.mixer.get_init()
            pygame.mixer.pre_init(22050, -16, 2, bufsize)
            pygame.mixer.init()
        except pygame.error as message:
            print('Sound initialization failed. %s' % message)
            no_sound = True

    playback_mode = PM_OFF
    record_challenge = 0
    playback_file = opts.get("--playback", None)
    if playback_file is not None:
        playback_mode = PM_PLAYBACK

    record_file = opts.get("--record", None)
    if record_file is not None:
        if playback_mode == PM_PLAYBACK:
            playback_mode = PM_PLAYTHRU
        else:
            playback_mode = PM_RECORD
            record_challenge = getattr(primitives,
                        "MENU_" + opts.get("--challenge",
                                    "BEGINNER").upper())

    pygame.init()
    pygame.font.init()

    if flags & FULLSCREEN:
        # Ensure that all resolutions are supported by the system
        for resolution in RESOLUTIONS:
            if resolution[:2] not in pygame.display.list_modes():
                RESOLUTIONS.remove(resolution)

        
    if ( no_sound ):
        resource.No_Sound()
    else:
        pygame.mixer.init(22050,-16,2,bufsize)

    res = opts.get("--resolution", "").split("x")
    if len(res) == 2:
        config.cfg.resolution = (int(res[0]), int(res[1]))

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(config.cfg.resolution, flags)
    height = screen.get_rect().height
    width = screen.get_rect().width

    # Icon
    # The icon provided in the Debian package is different than the original one
    # (size and location changed)
    if os.path.isfile(DEB_ICON):
        pygame.display.set_icon(resource.Load_Image(DEB_ICON))
    else:
        pygame.display.set_icon(resource.Load_Image("32.png"))

    # Game begins.. show loading image
    screen.fill((0,0,0))
    pygame.display.flip()
    pygame.display.set_caption(n)
    storms.Init_Storms()
    alien_invasion.Init_Aliens()
    quakes.Init_Quakes()

    quit = False
    if playback_mode != PM_OFF:
        # record/playback
        try:
            game.Main_Loop(screen=screen, clock=clock,
                    width_height=(width, height), restore_pos=None,
                    challenge=record_challenge,
                    playback_mode=playback_mode,
                    playback_file=playback_file,
                    record_file=record_file)
        except PlaybackEOF:
            print("End of playback")
        quit = True

    while ( not quit ):
        if ( config.cfg.resolution != (width, height) ):

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
    if not no_sound:
        pygame.mixer.quit()
    pygame.quit()


def Main_Menu_Loop(name, clock, screen, width_height):
    # Further initialisation
    (width, height) = width_height
    menu_image = resource.Load_Image("mainmenu.jpg")

    if ( menu_image.get_rect().width != width ):
        menu_image = pygame.transform.scale(menu_image, (width, height))

    stats.Set_Font_Scale(config.cfg.font_scale)

    main_menu = current_menu = menu.Menu([ 
                (None, None, []),
                (MENU_TUTORIAL, "Play Tutorial", []),
                (MENU_NEW_GAME, "Play New Game", []),
                (MENU_LOAD, "Restore Game", []),
                (None, None, []),
                (MENU_RES, "Set Graphics Resolution", []),
                (MENU_MUTE, "Toggle Sound", []),
                (MENU_MANUAL, "View Manual", []),
                (MENU_UPDATES, "Check for Updates", []),
                (None, None, []),
                (MENU_QUIT, "Exit to " + extra.Get_OS(), 
                    [ K_ESCAPE , K_F10 ])])
    resolution_menu = menu.Menu( 
                [(None, None, [])] + [
                (w, "%u x %u" % (w,h), [])
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
                (MENU_PEACEFUL, "Peaceful", []),
                (None, None, []),
                (-1, "Cancel", [])])

    copyright = [ name,
            "Copyright (C) Jack Whitham 2006-11 - website: www.jwhitham.org",
            None,
            "Game version " + config.CFG_VERSION ]

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
            img_r.center = (( width * 3 ) // 4, 0)
            img_r.clamp_ip(screen.get_rect())
            img_r.top = y
            screen.blit(img, img_r.topleft)
            y += img_r.height
       
        (quit, cmd) = extra.Simple_Menu_Loop(screen, current_menu,
                (( width * 3 ) // 4, 10 + ( height // 2 )))

        if ( current_menu == main_menu ):
            if ( cmd == MENU_NEW_GAME ):
                current_menu = difficulty_menu

            elif ( cmd == MENU_TUTORIAL ):
                quit = game.Main_Loop(screen=screen, clock=clock,
                        width_height=(width, height), restore_pos=None,
                        challenge=MENU_TUTORIAL,
                        playback_mode=PM_OFF,
                        playback_file=None,
                        record_file=None)

            elif ( cmd == MENU_LOAD ):
                current_menu = save_menu.Save_Menu(False)

            elif ( cmd == MENU_QUIT ):
                quit = True

            elif ( cmd == MENU_MUTE ):
                config.cfg.mute = not config.cfg.mute
                return False # update menu

            elif ( cmd == MENU_RES ):
                current_menu = resolution_menu

            elif ( cmd == MENU_UPDATES ):
                if Update_Feature(screen, menu_image):
                    url = ( CGISCRIPT + "v=" +
                            startup.Get_Game_Version() )

                    pygame.display.iconify()
                    try:
                        webbrowser.open(url, True, True)
                    except:
                        pass

            elif ( cmd == MENU_MANUAL ):
                pygame.display.iconify()
                if os.path.isfile(DEB_MANUAL):
                    # Debian manual present
                    url = 'file://' + DEB_MANUAL
                else:
                    base = os.path.abspath(resource.Path(os.path.join("..", 
                            "manual", "index.html")))
                    if os.path.isfile(base):
                        # Upstream package manual present
                        url = 'file://' + base
                    else:
                        # No manual? Redirect to website.
                        url = 'http://www.jwhitham.org/20kly/'

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
                    quit = game.Main_Loop(screen=screen, clock=clock,
                            width_height=(width, height), restore_pos=None,
                            challenge=cmd,
                            playback_mode=PM_OFF,
                            playback_file=None,
                            record_file=None)

            else: # Load menu
                if ( cmd >= 0 ):
                    # Start game from saved position
                    quit = game.Main_Loop(screen=screen, clock=clock,
                            width_height=(width, height), restore_pos=cmd,
                            challenge=None,
                            playback_mode=PM_OFF,
                            playback_file=None,
                            record_file=None)

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
    except Exception as x:
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




