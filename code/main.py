#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame , sys , math , time , webbrowser , urllib.request , os
import getopt


import game , stats , storms , extra , save_menu , resource , menu
import config , startup , sound , alien_invasion , quakes
from primitives import *
from game_types import *
from game_random import PlaybackEOF
import primitives
import sdl

DEB_ICON = '/usr/share/pixmaps/lightyears.xpm'
DEB_MANUAL = '/usr/share/doc/lightyears/html/index.html'


def Main(data_dir: str) -> None:

    n = "20,000 Light-Years Into Space"
    print("")
    print(n)
    print("Copyright (C) Jack Whitham 2006-21")
    print("Version " + startup.Get_Game_Version())
    print("")
    sys.stdout.flush()

    resource.DATA_DIR = data_dir

    (opts_list, args) = getopt.getopt(
            sys.argv[1:], "",
            ["safe",
                "no-sound", "playback=", "record=",
                "challenge="])
    opts = dict(opts_list)
    sys.stdout.flush()

    config.Initialise("--safe" in opts)

    # This allows the window to be scaled to any size
    # The game itself always uses a native resolution of 1024x768
    sdl.SDL_SetHintWithPriority("SDL_HINT_RENDER_SCALE_QUALITY", "best", 0)

    # Pygame things
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

    playback_mode: PlayMode = PlayMode.OFF
    record_challenge: Optional[MenuCommand] = None
    playback_file = opts.get("--playback", None)
    if playback_file is not None:
        playback_mode = PlayMode.PLAYBACK

    record_file = opts.get("--record", None)
    if record_file is not None:
        if playback_mode == PlayMode.PLAYBACK:
            playback_mode = PlayMode.PLAYTHRU
        else:
            playback_mode = PlayMode.RECORD
            record_challenge = MenuCommand(opts.get("--challenge", "BEGINNER").upper())

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
    if os.path.isfile(DEB_ICON):
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
                    challenge=record_challenge,
                    playback_mode=playback_mode,
                    playback_file=playback_file,
                    record_file=record_file)
        except PlaybackEOF:
            print("End of playback")
            return_code = 0

        quit = True

    while ( not quit ):
        quit = Main_Menu_Loop(n, clock, screen, (width, height))

    config.Save()

    # Bye bye Pygame.
    if not no_sound:
        pygame.mixer.quit()
    pygame.quit()
    sys.exit(return_code)


def Main_Menu_Loop(name: str, clock: ClockType, screen: SurfaceType,
                   width_height: SurfacePosition) -> bool:
    # Further initialisation
    (width, height) = width_height
    menu_image = resource.Load_Image("mainmenu.jpg")

    if ( menu_image.get_rect().width != width ):
        menu_image = pygame.transform.scale(menu_image, (width, height))

    main_menu = current_menu = menu.Menu([
                (None, None, []),
                (MenuCommand.TUTORIAL, "Play Tutorial", []),
                (MenuCommand.NEW_GAME, "Play New Game", []),
                (MenuCommand.LOAD, "Restore Game", []),
                (None, None, []),
                (MenuCommand.MUTE, "Toggle Sound", []),
                (MenuCommand.MANUAL, "View Manual", []),
                (MenuCommand.UPDATES, "Check for Updates", []),
                (None, None, []),
                (MenuCommand.QUIT, "Exit to " + extra.Get_OS(),
                    [ pygame.K_ESCAPE , pygame.K_F10 ])])
    difficulty_menu = menu.Menu(
                [(None, None, []),
                (MenuCommand.TUTORIAL, "Tutorial", []),
                (None, None, []),
                (MenuCommand.BEGINNER, "Beginner", []),
                (MenuCommand.INTERMEDIATE, "Intermediate", []),
                (MenuCommand.EXPERT, "Expert", []),
                (None, None, []),
                (MenuCommand.PEACEFUL, "Peaceful", []),
                (None, None, []),
                (MenuCommand.CANCEL, "Cancel", [])])

    copyright = [ name,
            "Copyright (C) Jack Whitham 2006-11 - website: www.jwhitham.org",
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

        (quit, cmd) = extra.Simple_Menu_Loop(screen, current_menu,
                (( width * 3 ) // 4, 10 + ( height // 2 )))

        if ( current_menu == main_menu ):
            if ( cmd == MenuCommand.NEW_GAME ):
                current_menu = difficulty_menu

            elif ( cmd == MenuCommand.TUTORIAL ):
                quit = game.Main_Loop(screen=screen, clock=clock,
                        width_height=(width, height), restore_pos=None,
                        challenge=MenuCommand.TUTORIAL,
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
                if Update_Feature(screen, menu_image):
                    url = ( CGISCRIPT + "v=" +
                            startup.Get_Game_Version() )

                    pygame.display.iconify()
                    try:
                        webbrowser.open(url, True, True)
                    except:
                        pass

            elif ( cmd == MenuCommand.MANUAL ):
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


        elif ( cmd is not None ):
            if ( current_menu == difficulty_menu ):
                if ( cmd != MenuCommand.CANCEL ):
                    quit = game.Main_Loop(screen=screen, clock=clock,
                            width_height=(width, height), restore_pos=None,
                            challenge=cmd,
                            playback_mode=PlayMode.OFF,
                            playback_file=None,
                            record_file=None)

            else: # Load menu
                if ( cmd != MenuCommand.CANCEL ):
                    # Start game from saved position
                    quit = game.Main_Loop(screen=screen, clock=clock,
                            width_height=(width, height),
                            restore_pos=cmd, challenge=None,
                            playback_mode=PlayMode.OFF,
                            playback_file=None,
                            record_file=None)

            current_menu = main_menu

    return True

def Update_Feature(screen: SurfaceType, menu_image: SurfaceType) -> bool:
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
            e = pygame.event.poll()
            while ( e.type != pygame.NOEVENT ):
                if (( e.type == pygame.MOUSEBUTTONDOWN )
                or ( e.type == pygame.KEYDOWN )
                or ( e.type == pygame.QUIT )):
                    ok = False
                e = pygame.event.poll()

            pygame.time.wait( 40 )
            timer -= 40

    Message(["Connecting to Website..."])
    url = ( CGISCRIPT + "a=1" )
    new_version = None
    try:
        f = urllib.request.urlopen(url)
        new_version_bytes = f.readline()
        new_version = new_version_bytes.decode("ascii")
        f.close()
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

        except Exception as x:
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
