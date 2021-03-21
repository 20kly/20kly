#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, sys, math, time, os
import getopt


from . import game, font, save_menu, resource, menu, events
from . import config, sound, alien_invasion, quakes, mail, version, compatibility
from .primitives import *
from .game_types import *
from .game_random import PlaybackEOF


def Main(data_dir: str, args: List[str], event: events.Events) -> int:

    print("")
    print(TITLE)
    print(COPYRIGHT)
    print("Version " + version.Encode(VERSION))
    print("", flush=True)

    resource.DATA_DIR = data_dir

    (opts_list, args) = getopt.getopt(
            args, "",
            ["safe",
                "no-sound", "playback=", "record=",
                "challenge=", "is-testing", "test-height="])
    opts = dict(opts_list)

    config.Initialise("--safe" in opts)
    mail.Initialise()

    # Pygame things
    bufsize = 2048

    event.is_testing = event.is_testing or ( "--is-testing" in opts )
    no_sound = ( "--no-sound" in opts)
    if not no_sound:
        try:
            pygame.mixer.get_init()
            pygame.mixer.pre_init(44100, -16, 2, bufsize)
            pygame.mixer.init()
        except pygame.error as message: # NO-COV
            print('Sound initialization failed. %s' % message)
            no_sound = True

    playback_mode: PlayMode = PlayMode.OFF
    record_challenge: Optional[MenuCommand] = None
    playback_file = opts.get("--playback", None)
    if playback_file is not None:
        playback_mode = PlayMode.PLAYBACK

    record_file = opts.get("--record", None)
    if record_file is not None:
        if playback_mode == PlayMode.PLAYBACK: # NO-COV
            playback_mode = PlayMode.PLAYTHRU
        else:
            playback_mode = PlayMode.RECORD
            record_challenge = MenuCommand[opts.get("--challenge",
                                        "BEGINNER").upper()]

    pygame.init()
    pygame.font.init()

    if no_sound:
        resource.No_Sound()
    else:
        pygame.mixer.init(44100,-16,2,bufsize)

    flags = pygame.RESIZABLE

    # Force a specific window height for testing purposes
    if "--test-height" in opts:
        height = int(opts["--test-height"])
        config.cfg.width = int(height * EXPECTED_ASPECT_RATIO)
        config.cfg.height = height
        config.Save()
        flags = 0

    resource.Initialise()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((config.cfg.width, config.cfg.height), flags)
    compatibility.last_resize = screen.get_rect().size
    mail.Set_Screen_Height(screen.get_rect().height)

    # Icon
    pygame.display.set_icon(resource.Load_Image(Images.i32))

    # Screensaver is not disabled
    compatibility.set_allow_screensaver(True)

    # Game begins.. show loading image
    screen.fill((0,0,0))
    pygame.display.flip()
    pygame.display.set_caption(TITLE)
    alien_invasion.Init_Aliens()
    quakes.Init_Quakes()

    quit = False
    return_code = 0
    if playback_mode != PlayMode.OFF:
        # record/playback
        try:
            return_code = 1 # Assume playback did not complete
            game.Game(clock=clock,
                    restore_pos=None,
                    challenge=record_challenge, event=event,
                    playback_mode=playback_mode,
                    playback_file=playback_file,
                    record_file=record_file).Main_Loop()
        except PlaybackEOF:
            print("End of playback")
            return_code = 0

        quit = True

    while ( not quit ):
        quit = Main_Menu_Loop(TITLE, clock, event)

    config.Save()

    # Bye bye Pygame.
    if event.is_testing:
        return return_code

    if not no_sound: # NO-COV
        pygame.mixer.quit()
    pygame.quit()
    if return_code != 0: # NO-COV
        sys.exit(return_code)

    return return_code


def Main_Menu_Loop(name: str, clock: ClockType,
                   event: events.Events) -> bool:

    current_menu: menu.Menu
    main_menu = menu.Toggle_Sound_Menu([
                (None, None, []),
                (MenuCommand.TUTORIAL, "Play Tutorial", [pygame.K_t]),
                (MenuCommand.NEW_GAME, "Play New Game", [pygame.K_n]),
                (MenuCommand.LOAD, "Restore Game", [pygame.K_r]),
                (None, None, []),
                menu.TOGGLE_SOUND,
                (MenuCommand.MANUAL, "View Manual", [pygame.K_v]),
                (MenuCommand.UPDATES, "Check for Updates", [pygame.K_u]),
                (None, None, []),
                (MenuCommand.QUIT, "Exit",
                    [ pygame.K_ESCAPE , pygame.K_F10 ])])
    difficulty_menu = menu.Menu(
                [(None, None, []),
                (MenuCommand.TUTORIAL, "Tutorial", [pygame.K_t]),
                (None, None, []),
                (MenuCommand.BEGINNER, "Beginner", [pygame.K_b]),
                (MenuCommand.INTERMEDIATE, "Intermediate", [pygame.K_i]),
                (MenuCommand.EXPERT, "Expert", [pygame.K_e]),
                (None, None, []),
                (MenuCommand.PEACEFUL, "Peaceful", [pygame.K_p]),
                (None, None, []),
                (MenuCommand.CANCEL, "Cancel", [pygame.K_ESCAPE])])
    current_menu = main_menu

    copyright = [ name,
            COPYRIGHT + " - website: www.jwhitham.org",
            "Game version " + version.Encode(VERSION) ]

    # off we go.

    menu_image = resource.Load_Image(Images.mainmenu)
    letters_image = resource.Load_Image(Images.letters).convert_alpha()

    quit = False
    while ( not quit ):
        # Main menu
        screen = event.resurface()
        (width, height) = screen.get_rect().size

        if ( menu_image.get_rect().width != width ): # NO-COV
            menu_image = pygame.transform.smoothscale(menu_image, (width, height))
        if ( letters_image.get_rect().height != height ): # NO-COV
            (w, h) = letters_image.get_rect().size
            w = int(w * (height / h))
            letters_image = pygame.transform.smoothscale(letters_image, (w, height))

        screen.blit(menu_image, (0,0))
        screen.blit(letters_image, (0,0))

        y = 5
        for text in copyright:
            img = font.Get_Font(11).render(text, True, (200, 200, 128))
            img_r = img.get_rect()
            img_r.center = (( width * 3 ) // 4, 0)
            img_r.clamp_ip(screen.get_rect())
            img_r.top = y
            screen.blit(img, img_r.topleft)
            y += img_r.height

        (quit, cmd) = menu.Simple_Menu_Loop(screen, current_menu,
                (( width * 3 ) // 4, 10 + ( height // 2 )), event)

        if ( current_menu == main_menu ):
            if ( cmd == MenuCommand.NEW_GAME ):
                current_menu = difficulty_menu

            elif ( cmd == MenuCommand.TUTORIAL ):
                quit = game.Game(clock=clock,
                        restore_pos=None,
                        challenge=MenuCommand.TUTORIAL, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None).Main_Loop()

            elif ( cmd == MenuCommand.LOAD ):
                current_menu = save_menu.Save_Menu(False)

            elif ( cmd == MenuCommand.QUIT ):
                quit = True

            elif ( cmd == MenuCommand.UPDATES ):
                if Update_Feature(menu_image, event):
                    url = ( CGISCRIPT + "v=" + version.Encode(VERSION) )

                    event.webbrowser_open(url)

            elif ( cmd == MenuCommand.MANUAL ):
                if os.path.isfile(DEB_MANUAL):
                    # Debian manual present
                    url = 'file://' + DEB_MANUAL  # NO-COV
                else:
                    base = os.path.abspath(resource.Path(os.path.join("..",
                            "manual", "index.html")))
                    if os.path.isfile(base):
                        # Upstream package manual present
                        url = 'file://' + base
                    else:
                        # No manual? Redirect to website.
                        url = 'http://www.jwhitham.org/20kly/'  # NO-COV

                event.webbrowser_open(url)

        elif ( current_menu == difficulty_menu ):
            if ( cmd != None ):
                current_menu = main_menu

            if (( cmd != None ) and ( cmd != MenuCommand.CANCEL )):
                # start new game with specified difficulty
                quit = game.Game(clock=clock,
                        restore_pos=None,
                        challenge=cmd, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None).Main_Loop()

        else: # Load menu
            if ( cmd != None ):
                current_menu = main_menu

            if (( cmd != None ) and ( cmd != MenuCommand.CANCEL )):
                # Start game from saved position
                quit = game.Game(clock=clock,
                        restore_pos=cmd, challenge=None, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None).Main_Loop()

    return True

def Update_Feature(menu_image: SurfaceType, event: events.Events) -> bool:
    screen = event.resurface()

    def Message(msg_list: List[str]) -> None:
        screen.blit(menu_image, (0,0))

        y = screen.get_rect().centery
        for msg in msg_list:
            img_1 = font.Get_Font(24).render(msg, True, (255, 255, 255))
            img_2 = font.Get_Font(24).render(msg, True, (0, 0, 0))
            img_r = img_1.get_rect()
            img_r.centerx = screen.get_rect().centerx
            img_r.centery = y
            screen.blit(img_2, img_r.topleft)
            screen.blit(img_1, img_r.move(2,-2).topleft)
            y += img_r.height
        pygame.display.flip()

    def Finish(cerror: Optional[str] = None) -> None:
        if ( cerror is not None ):
            Message(["Connection error:", cerror])

        ok = True
        timer = 4000
        while (( ok ) and ( timer > 0 )):
            e = event.poll()
            while ( e.type != pygame.NOEVENT ):
                if (( e.type == pygame.MOUSEBUTTONDOWN )
                or ( e.type == pygame.KEYDOWN )
                or ( e.type == pygame.QUIT )):
                    ok = False
                e = event.poll()

            if ok: # NO-COV
                pygame.time.wait( 40 )
                timer -= 40

    Message(["Connecting to Website..."])
    url = ( CGISCRIPT + "a=2" )
    new_version = None
    try:
        new_version = event.check_update(url)
    except Exception as x:
        Finish(str(x))
        return False

    if (( new_version is None )
    or ( type(new_version) != str )
    or ( len(new_version) < 2 )
    or ( len(new_version) > 10 )
    or ( not new_version[ 0 ].isdigit() )
    or ( new_version.find('.') <= 0 )):
        Finish("Version data not found.")
        return False


    new_version_int = version.Decode(new_version)
    new_version = version.Encode(new_version_int)
    old_version_int = VERSION
    old_version = version.Encode(old_version_int)

    if new_version_int == old_version_int:
        Message(["Your software is up to date!",
            "Thankyou for using the update feature."])
        Finish(None)
        return False
    elif new_version_int > old_version_int:
        Message(["New version " + new_version + " is available!",
                "Opening website..."])
        Finish(None)
        return True
    else:
        Message(["Your software is very up to date (beta?)",
            "'New' version is " + new_version + ": your version is " + old_version])
        Finish(None)
        return False
