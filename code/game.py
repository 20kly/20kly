#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#
#
# The main loop of the game. This procedure is running
# whenever the game is on the screen.

import pygame , sys , math , time , pickle

import bresenham , intersect , extra , stats , mail , gametime
import menu , startup , save_menu , save_game , config , resource
import review , sound , tutor , draw_obj
import game_random, grid
from primitives import *
from game_types import *
from quiet_season import Quiet_Season
import alien_invasion
from quakes import Quake_Season
from storms import Storm_Season
from steam_model import Steam_Model
from network import Network
from ui import User_Interface
from mail import New_Mail
from difficulty import DIFFICULTY


class Game_Data:
    def __init__(self, demo: "game_random.Game_Random", challenge: MenuCommand) -> None:
        self.version = startup.Get_Game_Version()
        self.sysinfo = extra.Get_System_Info()
        teaching = ( challenge == MenuCommand.TUTORIAL )

        # Steam network initialisation
        self.net = Network(demo, teaching)

        # Game variables
        self.season = Season.START
        self.season_ends = 0.0
        self.season_effect = 0.0
        self.season_fx = Quiet_Season(self.net)
        self.work_units_used = 0
        self.challenge = challenge
        self.difficulty_level = 1.0
        self.work_timer = 0.1
        self.game_ends_at: Optional[float] = None
        self.game_running = True
        self.game_time = gametime.Game_Time()
        self.historian: List[review.Historical_Record] = []
        self.historian_time = 0.0
        self.win = False
        self.warning_given = False
        self.wu_integral = 0

def Main_Loop(screen: SurfaceType, clock: ClockType, width_height: SurfacePosition,
              restore_pos: Optional[int], challenge: Optional[MenuCommand],
              playback_mode: PlayMode, playback_file: Optional[str],
              record_file: Optional[str]) -> bool:
    # Initialisation of screen things.

    (width, height) = width_height
    menu_margin = height
    screen.fill((0,0,0))  # screen is black during init
    pygame.display.flip()
    tutor.Off()

    draw_obj.Flush_Draw_Obj_Cache() # in case of resize

    # Grid setup
    (w,h) = GRID_SIZE
    assert w == h
    grid.Set_Grid_Size(height // h)

    # Windows..
    game_screen_rect = pygame.Rect(0, 0, menu_margin, height)
    game_screen_surf = screen.subsurface(game_screen_rect)
    menu_area = screen.subsurface(pygame.Rect(menu_margin, 0,
                        width - menu_margin, height))
    menu_width = width - menu_margin


    # Constraint on resolution applied here:
    assert menu_width >= 100

    def Sc(v):
        # Original values were for 800x600 - scale that
        # for whatever the user's screen res happens to be.
        return ( v * height ) / 600

    margin = Sc(10)
    x1 = menu_margin + margin
    menu_width1 = menu_width - ( margin * 2 )

    picture = resource.Load_Image("headersm.jpg")
    picture_rect = picture.get_rect().inflate(10,10)
    picture_rect.center = (x1 + ( menu_width1 // 2 ),0)
    picture_rect.top = margin
    picture_surf = screen.subsurface(picture_rect)

    stats_rect = pygame.Rect(x1, picture_rect.bottom + margin,
                menu_width1, Sc(120))
    stats_surf = screen.subsurface(stats_rect)
    global_stats_rect = pygame.Rect(x1, stats_rect.bottom + margin,
                menu_width1, Sc(110))
    global_stats_surf = screen.subsurface(global_stats_rect)
    controls_rect = pygame.Rect(x1, global_stats_rect.bottom + margin,
                menu_width1, height -
                    ( margin + global_stats_rect.bottom + margin ))
    controls_surf = screen.subsurface(controls_rect)

    def Special_Refresh():
        extra.Tile_Texture(screen, "rivets.jpg",
                pygame.Rect(menu_margin, 0,
                    menu_width, screen.get_rect().height))

        edge = pygame.Rect(menu_margin, -10,
            menu_width + 10, screen.get_rect().height + 10)

        for r in [ stats_rect, global_stats_rect, edge ]:
            extra.Line_Edging(screen, r, False)

        r = picture.get_rect()
        r.center = picture_surf.get_rect().center
        extra.Line_Edging(picture_surf, r, False)
        picture_surf.blit(picture, r.topleft)


    Special_Refresh()

    stats_surf.fill((0,0,0))

    FRAME_RATE = 35

    alarm_sound = sound.Persisting_Sound("emergency")
    demo = game_random.Game_Random()

    if playback_mode in (PlayMode.PLAYBACK, PlayMode.PLAYTHRU):
        assert playback_file is not None
        challenge = demo.begin_read(playback_file)

    if playback_mode in (PlayMode.PLAYTHRU, PlayMode.RECORD):
        assert record_file is not None
        assert challenge is not None
        demo.begin_write(record_file, challenge)

    assert challenge is not None

    # Game data holder
    g = Game_Data(demo, challenge)

    DIFFICULTY.Set(MenuCommand.INTERMEDIATE)

    # Establish equilibrium with initial network.
    for i in range(300):
        g.net.Steam_Think()
        if ( g.net.hub.Get_Pressure() >= PRESSURE_GOOD ):
            if ( DEBUG ):
                print(i,'steps required for equilibrium')
            break

    assert g.net.hub.Get_Pressure() >= PRESSURE_GOOD

    # UI setup
    ui = User_Interface(g.net, demo, (width,height))
    inputs = [
        (controls_rect, ui.Control_Mouse_Down, ui.Control_Mouse_Move),
        (game_screen_rect, ui.Game_Mouse_Down, ui.Game_Mouse_Move) ]
    exit_options: List[MenuItem] = [
        (MenuCommand.MENU, "Exit to Main Menu", []),
        (MenuCommand.QUIT, "Exit to " + extra.Get_OS(), [ pygame.K_F10 ])]

    save_available: List[MenuItem] = [(MenuCommand.SAVE, "Save Game", []),
        (MenuCommand.LOAD, "Restore Game", []),
        (None, None, [])]

    if ( challenge == MenuCommand.TUTORIAL ):
        save_available = []

    in_game_menu = menu.Menu(typing.cast(List[MenuItem], [
        (None, None, []),
        (MenuCommand.MUTE, "Toggle Sound", []),
        (None, None, [])]) +
        save_available + [
        (MenuCommand.HIDE, "Return to Game", [ pygame.K_ESCAPE ])] +
        exit_options)

    current_menu = in_game_menu

    flash = True
    loop_running = True
    quit = False
    stats_review = False
    in_game_menu.Select(None)
    mail.Initialise()
    rt_then = time.time()
    fps_count = 0
    fps_time = rt_then

    if ( restore_pos is None ):
        DIFFICULTY.Set(challenge)


    mail.Set_Day(g.game_time.Get_Day())

    def Summary(g):
        lev = dict()
        lev[ MenuCommand.TUTORIAL ] = "a Tutorial"
        lev[ MenuCommand.BEGINNER ] = "a Beginner"
        lev[ MenuCommand.INTERMEDIATE ] = "an Intermediate"
        lev[ MenuCommand.EXPERT ] = "an Expert"
        lev[ MenuCommand.PEACEFUL ] = "a Peaceful"

        assert g.challenge is not None
        assert lev.get( g.challenge, None )
        New_Mail("You are playing " + lev[ g.challenge ] + " game.")
        New_Mail("Win the game by upgrading your city to tech level %u."
                % DIFFICULTY.CITY_MAX_TECH_LEVEL )

    # Almost ready to start... but are we starting
    # from a savegame?
    def Restore(g, cmd):
        (g2, result) = save_game.Load(g, cmd)
        if ( result is None ):
            g = g2
            ui.net = g.net
            mail.Initialise()
            mail.Set_Day(g.game_time.Get_Day())
            assert g.challenge is not None
            DIFFICULTY.Set(g.challenge)
            New_Mail("Game restored. It is the " +
                g.season_fx.name + " season.")
        else:
            New_Mail(result)
        return g

    if ( restore_pos is not None ):
        g.challenge = MenuCommand.INTERMEDIATE
        g = Restore(g, restore_pos)

    assert g.challenge is not None
    Summary(g)

    if ( g.challenge == MenuCommand.TUTORIAL ):
        tutor.On(( menu_margin * 40 ) // 100)

    cur_time = g.game_time.time()

    # Main loop
    while ( loop_running ):

        if ( g.game_running ):
            flash = not flash
        menu_inhibit = ui.Is_Menu_Open() or not g.game_running


        if playback_mode in (PlayMode.PLAYBACK, PlayMode.PLAYTHRU):
            clock.tick(0)
        else:
            clock.tick(FRAME_RATE)

        rt_now = time.time()
        rt_frame_length = rt_now - rt_then
        rt_then = rt_now
        fps_count += 1
        if ( fps_count > 100 ):
            if ( DEBUG ):
                print('%1.2f fps' % ( float(fps_count) / ( rt_now - fps_time ) ))
            fps_time = rt_now
            fps_count = 0

        if playback_mode != PlayMode.OFF:
            rt_frame_length = 1.0 / FRAME_RATE

        if ( not menu_inhibit ):
            if ( not tutor.Frozen () ):
                g.game_time.Advance(rt_frame_length)
            draw_obj.Next_Frame() # Flashing lights on the various items

        cur_time = g.game_time.time()
        mail.Set_Day(g.game_time.Get_Day())

        if ( not menu_inhibit ):
            demo.timestamp(g)

        ui.Draw_Game(game_screen_surf, g.season_fx)

        #if ( flash ):
        #ui.Draw_Selection(picture_surf)

        until_next: List[StatTuple]
        if ( g.challenge == MenuCommand.TUTORIAL ):
            until_next = []
        elif ( g.challenge == MenuCommand.PEACEFUL ):
            until_next = [ ((128,128,128), 12, "Peaceful mode") ]
        else:
            until_next = [ ((128,128,128), 12, "(%d days until next season)" %
                        (( g.season_ends - cur_time ) + 1 )) ]

        ui.Draw_Stats(stats_surf, typing.cast(List[StatTuple], [
              ((128,0,128), 18, "Day %u" % g.game_time.Get_Day()),
              ((128,128,0), 18, g.season_fx.name + " season") ]) +
              until_next +
                g.season_fx.Get_Extra_Info())
        ui.Draw_Controls(controls_surf)

        if ( menu_inhibit ):
            current_menu.Draw(screen)
            alarm_sound.Set(0.0)

        stats_back = (0,0,0)
        supply = g.net.hub.Get_Steam_Supply()
        demand = g.net.hub.Get_Steam_Demand()
        if ( g.net.hub.Get_Pressure() < PRESSURE_DANGER ):
            # You'll lose the game if you stay in this zone
            # for longer than a timeout. Also, an
            # alarm will sound.

            if ( g.game_ends_at is None ):
                sound.FX("steamcrit")
                g.warning_given = True

                New_Mail("Danger! The City needs more steam!", (255,0,0))
                g.game_ends_at = cur_time + DIFFICULTY.GRACE_TIME
                assert g.game_ends_at is not None
                New_Mail("Game will end on Day %u unless supplies are increased." % (
                    int(g.game_ends_at) ), (255,0,0))

            if ( flash ):
                demand_colour = (255, 0, 0)
                if ( not menu_inhibit ):
                    alarm_sound.Set(0.6)
            else:
                demand_colour = (128, 0, 0)
                stats_back = (100, 0, 0)

        elif ( g.net.hub.Get_Pressure() < PRESSURE_WARNING ):

            g.game_ends_at = None
            if ( flash ):
                demand_colour = (255, 100, 0)
                if ( not menu_inhibit ):
                    alarm_sound.Set(0.3)
            else:
                demand_colour = (128, 50, 0)
                stats_back = (50, 25, 0)
        else:

            if ( g.warning_given ):
                sound.FX("steamres")
                g.warning_given = False

            if ( g.net.hub.Get_Pressure() < PRESSURE_OK ):
                demand_colour = (128, 128, 0)
            else:
                demand_colour = (0, 128, 0)

            g.game_ends_at = None
            alarm_sound.Set(0.0)

        avw = g.net.hub.Get_Avail_Work_Units()
        wu_unused = avw - g.work_units_used
        if ( not menu_inhibit ):
            global_stats_surf.fill(stats_back)
            stats.Draw_Stats_Window(global_stats_surf, [
                  (CITY_COLOUR, 18, "Work Units Available"),
                  (None, None, (wu_unused, (255,0,255),
                              avw, (0,0,0))),
                  (CITY_COLOUR, 12, str(wu_unused) + " of " +
                          str(avw) + " total"),
                  (CITY_COLOUR, 18, "City - Supply:Demand"),
                  (demand_colour, 24, "%1.1f U : %1.1f U" % (
                            supply, demand)),
                  (CITY_COLOUR, 18, "City - Steam Pressure"),
                  (None, None, g.net.hub.Get_Pressure_Meter())])

        if ( g.challenge == MenuCommand.TUTORIAL ):
            tutor.Draw(screen, g)

        pygame.display.flip()

        if ( not menu_inhibit ):
            g.season_fx.Per_Frame(rt_frame_length)
            ui.Frame_Advance(rt_frame_length)

        # Timing effects
        if ( g.work_timer <= cur_time ):
            # Fixed periodic effects
            g.work_timer = cur_time + 0.1
            g.wu_integral += wu_unused
            g.work_units_used = g.net.Work_Pulse(g.net.hub.Get_Avail_Work_Units())

            g.net.Steam_Think()
            g.net.Expire_Popups()
            tutor.Examine_Game(g)

        if ( g.season_effect <= cur_time ):
            # Seasonal periodic effects
            g.season_effect = cur_time + g.season_fx.Get_Period()
            g.season_fx.Per_Period()

        if ((( not tutor.Permit_Season_Change() )
        and ( g.season == Season.QUIET ))
        or ( g.challenge == MenuCommand.PEACEFUL )):
            g.season_ends = cur_time + 2.0

        if ( g.season_ends <= cur_time ):
            # Season change
            if ( g.season == Season.START ):
                g.season = Season.QUIET
                g.season_fx = Quiet_Season(g.net)
            elif (( g.season == Season.QUIET )
            or ( g.season == Season.STORM )):
                g.season = Season.ALIEN
                g.season_fx = alien_invasion.Alien_Season(g.net, g.difficulty_level)
                sound.FX("aliensappr")
            elif ( g.season == Season.ALIEN ):
                g.season = Season.QUAKE
                g.season_fx = Quake_Season(g.net, g.difficulty_level)
                if ( not tutor.Active() ): # hack...
                    sound.FX("quakewarn")
            elif ( g.season == Season.QUAKE ):
                g.season = Season.STORM
                g.season_fx = Storm_Season(g.net, g.difficulty_level)
                g.difficulty_level *= 1.2 # 20% harder..
                sound.FX("stormwarn")
            else:
                assert False
            g.season_ends = cur_time + LENGTH_OF_SEASON
            g.season_effect = cur_time + ( g.season_fx.Get_Period() / 2 )

            if ( g.challenge != MenuCommand.PEACEFUL ):
                New_Mail("The " + g.season_fx.name +
                                " season has started.", (200,200,200))

        just_ended = False
        if (( g.game_ends_at is not None )
        and ( g.game_ends_at <= cur_time )
        and ( g.game_running )):
            # Game over - you lose
            g.game_running = False
            New_Mail("The City ran out of steam.", (255,0,0))
            New_Mail("Game Over!", (255,255,0))
            sound.FX("krankor")
            just_ended = True

        elif (( g.net.hub.tech_level >= DIFFICULTY.CITY_MAX_TECH_LEVEL )
        and ( g.game_running )):
            # Game over - you win!
            g.game_running = False
            g.win = True
            New_Mail("The City is now fully upgraded!", (255,255,255))
            New_Mail("You have won the game!", (255,255,255))
            sound.FX("applause")
            just_ended = True

        if ( just_ended ):
            current_menu = in_game_menu = menu.Menu(typing.cast(List[MenuItem], [
                (None, None, []),
                (MenuCommand.REVIEW, "Review Statistics", [])]) +
                exit_options)
            in_game_menu.Select(None)

        if ( not menu_inhibit ):
            demo.do_user_actions(ui)

        # Events
        e = pygame.event.poll()
        while ( e.type != pygame.NOEVENT ):
            if e.type == pygame.QUIT:
                loop_running = False
                quit = True

            elif playback_mode in (PlayMode.PLAYBACK, PlayMode.PLAYTHRU):
                pass

            elif (( e.type == pygame.MOUSEBUTTONDOWN )
            or ( e.type == pygame.MOUSEMOTION )):
                if (( e.type == pygame.MOUSEBUTTONDOWN )
                and ( e.button != 1 )):
                    if ( not menu_inhibit ):
                        ui.Right_Mouse_Down()

                elif ( not menu_inhibit ):
                    for (rect, click, move) in inputs:
                        if ( rect.collidepoint(e.pos)):
                            (x,y) = e.pos
                            x -= rect.left
                            y -= rect.top
                            if ( e.type == pygame.MOUSEMOTION ):
                                move((x,y))
                            else:
                                click((x,y))
                elif ( menu_inhibit ):
                    if ( e.type == pygame.MOUSEMOTION ):
                        current_menu.Mouse_Move(e.pos)
                    else:
                        current_menu.Mouse_Down(e.pos)

            elif e.type == pygame.KEYDOWN:
                if ( not menu_inhibit ):
                    ui.Key_Press(e.key)

                elif ( menu_inhibit ):
                    current_menu.Key_Press(e.key)

                if ( DEBUG or playback_mode != PlayMode.OFF ):
                    # Cheats.
                    if ( e.key == pygame.K_F10 ):
                        New_Mail("SEASON ADVANCE CHEAT")
                        g.season_ends = 0
                    elif ( e.key == pygame.K_F9 ):
                        screen.fill((255,255,255))
                    elif ( e.key == pygame.K_F8 ):
                        # Lose the game cheat
                        # Heh, worst cheat ever.
                        g.game_ends_at = cur_time

            e = pygame.event.poll()

        # Any commands from the menu?
        if ( menu_inhibit ):
            cmd = current_menu.Get_Command()
            current_menu.Select(None) # consume command

            if ( current_menu == in_game_menu ):

                # It's the normal menu.
                if ( cmd == MenuCommand.QUIT ):
                    loop_running = False
                    quit = True
                    ui.Reset() # makes menu disappear

                elif ( cmd == MenuCommand.MENU ):
                    loop_running = False
                    ui.Reset()

                elif ( cmd == MenuCommand.SAVE ):
                    if ( g.game_running ):
                        # Switch to alternate menu
                        current_menu = save_menu.Save_Menu(True)

                elif ( cmd == MenuCommand.LOAD ):
                    current_menu = save_menu.Save_Menu(False)

                elif ( cmd == MenuCommand.MUTE ):
                    config.cfg.mute = not config.cfg.mute
                    ui.Reset()

                elif ( cmd == MenuCommand.REVIEW ):
                    loop_running = False
                    stats_review = True
                    ui.Reset()

                elif ( cmd is not None ):
                    # Default option - back to game
                    if ( not g.game_running ):
                        New_Mail("Sorry - the game has finished")
                    ui.Reset()

            else:
                # It's another menu! That means it's the save menu.
                assert isinstance(current_menu, save_menu.Save_Menu)
                if (( cmd is not None )
                and ( cmd != MenuCommand.UNUSED )
                and ( cmd != MenuCommand.CANCEL )):
                    if ( not current_menu.Is_Saving() ):
                        g = Restore(g, cmd)

                    else:
                        label = "Day %u - %s season - %s" % (g.game_time.Get_Day(),
                                g.season_fx.name, time.asctime())

                        g.net.Make_Ready_For_Save()
                        result = save_game.Save(g, cmd, label)
                        if ( result is None ):
                            New_Mail("Game saved.")
                        else:
                            New_Mail(result)

                if ( cmd is not None ):
                    # Back to game.
                    Special_Refresh()
                    current_menu = in_game_menu
                    ui.Reset()

        if (( g.historian_time <= cur_time )
        and ( g.game_running )
        and ( not menu_inhibit )):
            g.historian.append(review.Analyse_Network(g))
            g.historian_time = cur_time + 4

    tutor.Off()

    # About to exit. Blackout.
    screen.fill((0,0,0))

    if ( stats_review ):
        review.Review(screen, (width, height), g, g.historian)

    return quit

