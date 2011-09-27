# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


import pygame , sys , time , webbrowser , urllib , os
from pygame.locals import *

import game , storms , extra , save_menu , resource , menu , screen , review
import config , startup , sound , alien_invasion , quakes , font , save_game
import trig, lp
from primitives import *
from colours import *

NAME = "20,000 Light-Years Into Space"

DEB_ICON = '/usr/share/pixmaps/lightyears.xpm'
DEB_MANUAL = '/usr/share/doc/lightyears/html/index.html'


def Main(data_dir):
    print ""
    print NAME 
    print "Copyright (C) Jack Whitham 2006-2011"
    print "Version", startup.Get_Game_Version()
    print ""

    config.Initialise(data_dir, "--safe" in sys.argv)
    trig.Initialise()
    lp.Initialise()

    # Pygame things
    bufsize = 2048

    no_sound = ( "--no-sound" in sys.argv )
    if ( not no_sound ):
        try:
            pygame.mixer.pre_init(22050,-16,2,bufsize)
        except pygame.error, message:
            print 'Sound initialisation failed. %s' % message
            no_sound = True

    pygame.init()
    pygame.font.init()

    if ( no_sound ):
        resource.No_Sound()
    else:
        try:
            pygame.mixer.init(22050,-16,2,bufsize)
        except pygame.error, message:
            no_sound = True

    screen.Initialise()

    # Icon & window title
    if os.path.isfile(DEB_ICON):
        icon = resource.Load_Image(DEB_ICON)
    else:
        icon = resource.Load_Image("lightyears.png")

    pygame.display.set_icon(icon)
    pygame.display.set_caption(NAME)

    # Game begins.. show loading image
    screen.surface.fill(BLACK)

    img = font.Get_Font(12).render("Starting...", True, GREY)
    r = img.get_rect()
    r.center = screen.surface.get_rect().center
    screen.surface.blit(img, r.topleft)

    pygame.display.flip()
    storms.Init_Storms()
    alien_invasion.Init_Aliens()
    quakes.Init_Quakes()

    cmd = None
    while cmd != MENU_QUIT:
        cmd = Main_Menu_Loop()
        while cmd == MENU_RESIZE_EVENT:
            cmd = Main_Menu_Loop()

        if cmd in [ MENU_TUTORIAL, MENU_BEGINNER,
                MENU_INTERMEDIATE, MENU_EXPERT ]:
            # New game
            game.Create_Game(cmd)
            cmd = game.Main_Loop(None)

        elif 0 <= cmd < save_game.NUM_SLOTS:
            # Restore game
            game.Create_Game(MENU_INTERMEDIATE)
            cmd = game.Main_Loop(cmd)

        while cmd in (MENU_CONTINUE, MENU_RESIZE_EVENT):
            # Game continues
            cmd = game.Main_Loop(None)

        if cmd == MENU_REVIEW:
            # End of game review screen
            review.Review()
    

    config.Save()

    # Bye bye Pygame.
    pygame.mixer.quit()
    pygame.quit()


def Main_Menu_Loop():
    # Update resolution
    (width, height) = screen.Update_Resolution()

    # Further initialisation
    menu_image = resource.Load_Image("mainmenu.jpg")
    menu_rect = menu_image.get_rect()
    sr = screen.surface.get_rect()

    if menu_rect.size != sr.size:
        menu_rect = menu_rect.fit(sr)
        menu_image = pygame.transform.scale(menu_image, menu_rect.size)

    font.Scale_Font(height)

    main_menu = current_menu = menu.Menu([ 
                (None, None, []),
                (MENU_TUTORIAL, "Play Tutorial", []),
                (MENU_NEW_GAME, "Play New Game", []),
                (MENU_LOAD, "Restore Game", []),
                (None, None, []),
                (MENU_MUTE, "Toggle Sound", []),
                (MENU_MANUAL, "View Manual", []),
                (MENU_UPDATES, "Check for Updates", []),
                (None, None, []),
                (MENU_QUIT, "Exit to " + extra.Get_OS(), 
                    [ K_ESCAPE , K_F10 ])])
    difficulty_menu = menu.Menu( 
                [(None, None, []),
                (MENU_TUTORIAL, "Tutorial", []),
                (None, None, []),
                (MENU_BEGINNER, "Beginner", []),
                (MENU_INTERMEDIATE, "Intermediate", []),
                (MENU_EXPERT, "Expert", []),
                (None, None, []),
                (-1, "Cancel", [])])

    copyright = [ NAME,
            "Copyright (C) Jack Whitham 2006-11 - website: www.jwhitham.org",
            None,
            "Game version " + startup.Get_Game_Version() ]

    # off we go.

    while True:
        # Main menu loop
        screen.surface.fill(BLACK)
        screen.surface.blit(menu_image, menu_rect.topleft)
      
        y = 5
        sz = 11
        for text in copyright:
            if ( text == None ):
                sz = 7
                continue
            img = font.Get_Font(sz).render(text, True, COPYRIGHT)
            img_r = img.get_rect()
            img_r.center = (( width * 3 ) / 4, 0)
            img_r.clamp_ip(screen.surface.get_rect())
            img_r.top = y
            screen.surface.blit(img, img_r.topleft)
            y += img_r.height
       
        (quit, cmd) = extra.Simple_Menu_Loop(current_menu,
                (( width * 3 ) / 4, 10 + ( height / 2 )))

        if ( quit ):
            return MENU_QUIT

        if ( cmd == MENU_RESIZE_EVENT ):
            # Sent to outer loop, reinitialisation will be required
            return MENU_RESIZE_EVENT

        elif ( current_menu == main_menu ):
            if ( cmd == MENU_NEW_GAME ):
                current_menu = difficulty_menu

            elif ( cmd == MENU_TUTORIAL ):
                return MENU_TUTORIAL

            elif ( cmd == MENU_LOAD ):
                current_menu = save_menu.Save_Menu(False)

            elif ( cmd == MENU_QUIT ):
                return MENU_QUIT

            elif ( cmd == MENU_MUTE ):
                config.cfg.mute = not config.cfg.mute

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

                pygame.display.iconify()
                try:
                    webbrowser.open(url, True, True)
                except:
                    pass

        elif ( cmd != None ):
            if ( current_menu == difficulty_menu ):
                if ( cmd >= 0 ):
                    # Start game at specified difficulty
                    return cmd

            else: # Load menu
                if ( cmd >= 0 ):
                    # Start game from saved position
                    return cmd

            current_menu = main_menu 

def Update_Feature(menu_image, menu_rect):
    def Message(msg_list):
        screen.surface.blit(menu_image, menu_rect.topleft)

        y = screen.surface.get_rect().centery
        for msg in msg_list:
            img_1 = font.Get_Font(24).render(msg, True, WHITE)
            img_2 = font.Get_Font(24).render(msg, True, BLACK)
            img_r = img_1.get_rect()
            img_r.centerx = screen.surface.get_rect().centerx
            img_r.centery = y
            screen.surface.blit(img_2, img_r.topleft)
            screen.surface.blit(img_1, img_r.move(2,-2).topleft)
            y += img_r.height
        pygame.display.flip()

    def Finish(cerror=None):
        if ( cerror != None ):
            Message(["Connection error:", cerror])

        ok = True
        timer = 4000
        while (( ok ) and ( timer > 0 )):
            e = screen.Get_Event(False)
            while ( e.type != NOEVENT ):
                if (( e.type == MOUSEBUTTONDOWN )
                or ( e.type == KEYDOWN )
                or ( e.type == QUIT )):
                    ok = False
                e = screen.Get_Event(False)

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





