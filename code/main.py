#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, sys, math, time, os
import getopt


from . import game, stats, storms, save_menu, resource, menu, events
from . import config, startup, sound, alien_invasion, quakes, sdl, mail
from .primitives import *
from .game_types import *
from .game_random import PlaybackEOF


def Main(data_dir: str, args: List[str], event: events.Events) -> int:

    n = "20,000 Light-Years Into Space"
    print("")
    print(n)
    print("Copyright (C) Jack Whitham 2006-21")
    print("Version " + startup.Get_Game_Version())
    print("", flush=True)

    resource.DATA_DIR = data_dir

    (opts_list, args) = getopt.getopt(
            args, "",
            ["safe",
                "no-sound", "playback=", "record=",
                "challenge=", "is-testing"])
    opts = dict(opts_list)

    config.Initialise("--safe" in opts)
    mail.Initialise()

    # This allows the window to be scaled to any size
    # The game itself always uses a native resolution of 1024x768
    sdl.SDL_SetHintWithPriority("SDL_HINT_RENDER_SCALE_QUALITY", "nearest", 0)

    # Pygame things
    bufsize = 2048

    event.is_testing = event.is_testing or ( "--is-testing" in opts )
    no_sound = ( "--no-sound" in opts)
    if not no_sound:
        try:
            pygame.mixer.get_init()
            pygame.mixer.pre_init(22050, -16, 2, bufsize)
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

    if ( no_sound ):
        resource.No_Sound()
    else:
        pygame.mixer.init(22050,-16,2,bufsize)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.RESIZABLE)
    height = screen.get_rect().height
    width = screen.get_rect().width

    # Icon
    # The icon provided in the Debian package is different than the original one
    # (size and location changed)
    if os.path.isfile(DEB_ICON): # NO-COV
        pygame.display.set_icon(resource.Load_Image(DEB_ICON))
    else:
        pygame.display.set_icon(resource.Load_Image("32.png"))

    # Screensaver is not disabled
    pygame.display.set_allow_screensaver(True)

    # Game begins.. show loading image
    screen.fill((0,0,0))
    pygame.display.flip()
    pygame.display.set_caption(n)
    storms.Init_Storms()
    alien_invasion.Init_Aliens()
    quakes.Init_Quakes()

    quit = False
    return_code = 0
    if playback_mode != PlayMode.OFF:
        # record/playback
        try:
            return_code = 1 # Assume playback did not complete
            game.Main_Loop(screen=screen, clock=clock,
                    width_height=(width, height), restore_pos=None,
                    challenge=record_challenge, event=event,
                    playback_mode=playback_mode,
                    playback_file=playback_file,
                    record_file=record_file)
        except PlaybackEOF:
            print("End of playback")
            return_code = 0

        quit = True

    while ( not quit ):
        quit = Main_Menu_Loop(n, clock, screen, (width, height), event)

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


def Main_Menu_Loop(name: str, clock: ClockType, screen: SurfaceType,
                   width_height: SurfacePosition, event: events.Events) -> bool:
    # Further initialisation
    (width, height) = width_height
    menu_image = resource.Load_Image("mainmenu.jpg")

    main_menu = current_menu = menu.Menu([
                (None, None, []),
                (MenuCommand.TUTORIAL, "Play Tutorial", [pygame.K_t]),
                (MenuCommand.NEW_GAME, "Play New Game", [pygame.K_n]),
                (MenuCommand.LOAD, "Restore Game", [pygame.K_r]),
                (None, None, []),
                (MenuCommand.MUTE, "Toggle Sound", [pygame.K_m]),
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

    copyright = [ name,
            "Copyright (C) Jack Whitham 2006-21 - website: www.jwhitham.org",
            "",
            "Game version " + startup.Get_Game_Version() ]

    # off we go.

    quit = False
    while ( not quit ):
        # Main menu
        screen.fill((0,0,0))
        screen.blit(menu_image, (0,0))

        y = 5
        sz = 11
        for text in copyright:
            if ( text == "" ):
                sz = 7
                continue
            img = stats.Get_Font(sz).render(text, True, (200, 200, 128))
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
                quit = game.Main_Loop(screen=screen, clock=clock,
                        width_height=(width, height), restore_pos=None,
                        challenge=MenuCommand.TUTORIAL, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None)

            elif ( cmd == MenuCommand.LOAD ):
                current_menu = save_menu.Save_Menu(False)

            elif ( cmd == MenuCommand.QUIT ):
                quit = True

            elif ( cmd == MenuCommand.MUTE ):
                config.cfg.mute = not config.cfg.mute
                return False # update menu

            elif ( cmd == MenuCommand.UPDATES ):
                if Update_Feature(screen, menu_image, event):
                    url = ( CGISCRIPT + "v=" +
                            startup.Get_Game_Version() )

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
            if ( cmd != MenuCommand.CANCEL ):
                # start new game with specified difficulty
                quit = game.Main_Loop(screen=screen, clock=clock,
                        width_height=(width, height), restore_pos=None,
                        challenge=cmd, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None)

            current_menu = main_menu

        else: # Load menu
            if ( cmd != MenuCommand.CANCEL ):
                # Start game from saved position
                quit = game.Main_Loop(screen=screen, clock=clock,
                        width_height=(width, height),
                        restore_pos=cmd, challenge=None, event=event,
                        playback_mode=PlayMode.OFF,
                        playback_file=None,
                        record_file=None)

            current_menu = main_menu

    return True

def Update_Feature(screen: SurfaceType, menu_image: SurfaceType, event: events.Events) -> bool:
    def Message(msg_list: List[str]) -> None:
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
    url = ( CGISCRIPT + "a=1" )
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


    def Decode(version: str) -> Tuple[int, int]:
        version_code = version.strip().split(".")

        try:
            major = int(version_code[0], 10)
            minor = int(version_code[1], 10)
            return (major, minor)

        except Exception as x: # NO-COV
            return (0, 0)

    old_version = startup.Get_Game_Version()
    old_version_pair = Decode(old_version)
    new_version_pair = Decode(new_version)
    new_version = "{}.{}".format(*new_version_pair)

    if new_version_pair == old_version_pair:
        Message(["Your software is up to date!",
            "Thankyou for using the update feature."])
        Finish(None)
        return False
    elif new_version_pair > old_version_pair:
        Message(["New version " + new_version + " is available!",
                "Opening website..."])
        Finish(None)
        return True
    else:
        Message(["Your software is very up to date (beta?)",
            "'New' version is " + new_version + ": your version is " + old_version])
        Finish(None)
        return False
