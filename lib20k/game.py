#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#
#
# The main loop of the game. This procedure is running
# whenever the game is on the screen.

import pygame, sys, time, pickle, random, os, math

from . import draw_effects, stats, mail, gametime, events
from . import menu, save_menu, save_game, config, resource
from . import review, sound, tutor, draw_obj, compatibility
from . import game_random, grid, alien_invasion
from .primitives import *
from .game_types import *
from .quiet_season import Quiet_Season
from .quakes import Quake_Season
from .storms import Storm_Season
from .steam_model import Steam_Model
from .network import Network
from .ui import User_Interface
from .mail import New_Mail
from .difficulty import DIFFICULTY
from . import unit_test

FRAME_RATE = 35
RT_FRAME_LENGTH = 1.0 / FRAME_RATE

class Game_Data:
    def __init__(self, demo: "game_random.Game_Random", challenge: MenuCommand) -> None:
        self.version = VERSION
        self.sysinfo = config.Get_System_Info()
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
        self.backdrop_rotation = random.randrange(0, 8)

    def Pre_Save(self) -> None:
        self.net.Pre_Save()

    def Post_Load(self) -> None:
        self.net.Post_Load()


class Game:
    def __init__(self, event: events.Events, clock: ClockType,
              restore_pos: Optional[MenuCommand], challenge: Optional[MenuCommand],
              playback_mode: PlayMode, playback_file: Optional[str],
              record_file: Optional[str]) -> None:

        self.clock = clock
        self.event = event
        self.demo = game_random.Game_Random()
        self.playback_mode = playback_mode
        self.playback_file = playback_file
        self.record_file = record_file
        self.restore_pos = restore_pos

        # Initial black screen
        self.screen = self.event.resurface()
        self.screen.fill((0,0,0))
        pygame.display.flip()

        # Game data holder

        if (self.restore_pos is not None) or (challenge is None):
            challenge = MenuCommand.INTERMEDIATE

        if self.playback_mode == PlayMode.PLAYBACK:
            assert playback_file is not None
            self.demo = game_random.Play_and_Record()
            challenge = self.demo.begin_read(playback_file)

        elif self.playback_mode == PlayMode.RECORD:
            assert record_file is not None
            assert challenge is not None
            self.demo = game_random.Play_and_Record()
            self.demo.begin_write(record_file, challenge)

        elif self.playback_mode == PlayMode.PLAYTHRU:  # NO-COV
            assert playback_file is not None
            assert record_file is not None
            self.demo = game_random.Play_and_Record()
            challenge = self.demo.begin_read(playback_file)
            self.demo.begin_write(record_file, challenge)

        assert challenge is not None
        self.g = g = Game_Data(self.demo, challenge)

        # Fixed background in test modes (making screenshot comparisons easier)
        if (self.playback_mode != PlayMode.OFF) or self.event.is_testing: # NO-COV
            g.backdrop_rotation = 0

        # Establish equilibrium with initial network.
        DIFFICULTY.Set(MenuCommand.INTERMEDIATE)
        i = 300
        while i > 0:
            g.net.Steam_Think()
            if ( g.net.hub.Get_Pressure() >= PRESSURE_GOOD ):
                i = 0
            else:
                i -= 1

        assert g.net.hub.Get_Pressure() >= PRESSURE_GOOD

        # Switch to the difficulty level requested by the user
        DIFFICULTY.Set(challenge)

        # always have at least one item in history
        g.historian.append(review.Analyse_Network(g))

        # initialise mail
        mail.Initialise()
        mail.Set_Day(g.game_time.Get_Day())

        tutor.Off()

        # load pictures
        self.header_picture = resource.Load_Image(Images.headersm).convert()
        self.back_picture = resource.Load_Image(Images.back).convert()

        # create user interface
        self.ui = User_Interface(self.g.net, self.demo)

        # initialise the UI
        self.Recreate_UI()

    def Recreate_UI(self) -> None:
        g = self.g
        self.screen = self.event.resurface()
        self.size = self.screen.get_rect().size
        (width, height) = self.size
        self.menu_margin = height

        # Needed when resized
        draw_obj.Flush_Draw_Obj_Cache()

        # Windows..
        self.game_screen_rect = pygame.Rect(0, 0, self.menu_margin, height)
        self.game_screen_surf = self.screen.subsurface(self.game_screen_rect)
        self.menu_width = width - self.menu_margin


        # Constraint on resolution applied here:
        assert self.menu_width >= 100

        # Original values were for 800x600 - scale that
        # for whatever the user's screen res happens to be.
        sc = height / 600.0

        self.margin = margin = int(sc * 10)
        x1 = self.menu_margin + margin
        menu_width1 = self.menu_width - ( margin * 2 )

        self.scaled_header_picture = draw_effects.Scale_Image(self.header_picture)
        self.picture_rect = self.scaled_header_picture.get_rect().inflate(margin, margin)
        self.picture_rect.center = (x1 + ( menu_width1 // 2 ),0)
        self.picture_rect.top = margin
        self.picture_surf = self.screen.subsurface(self.picture_rect)

        self.stats_rect = pygame.Rect(x1, self.picture_rect.bottom + margin,
                    menu_width1, int(sc * 120))
        self.stats_surf = self.screen.subsurface(self.stats_rect)
        self.global_stats_rect = pygame.Rect(x1, self.stats_rect.bottom + margin,
                    menu_width1, int(sc * 110))
        self.global_stats_surf = self.screen.subsurface(self.global_stats_rect)
        self.controls_rect = pygame.Rect(x1, self.global_stats_rect.bottom + margin,
                    menu_width1, height -
                        ( margin + self.global_stats_rect.bottom + margin ))
        self.controls_surf = self.screen.subsurface(self.controls_rect)

        self.Special_Refresh()

        self.stats_surf.fill((0,0,0))

        # Background image for user interface
        img = self.back_picture

        # Although there is only one base image, it is flipped and
        # rotated on startup to create one of eight possible backdrops.
        img = pygame.transform.rotate(img, 90 * (g.backdrop_rotation // 2))
        if ( g.backdrop_rotation % 2 ) == 0: # NO-COV
            img = pygame.transform.flip(img, True, False)

        # How big should the background be?
        # * game_screen_rect().size -> it scales with the screen, not with the grid :(
        # * Grid_To_Scr(GRID_SIZE) -> there can be a black border between game area and menu
        # The size of this border is (game_screen_rect().size % GRID_SIZE) / Grid_To_Scr(1)
        # which is at its maximum at MINIMUM_HEIGHT. This maximum is:
        border_size = (GRID_SIZE[0] - 1) / (MINIMUM_HEIGHT // GRID_SIZE[0])
        # Adding this to the grid size tells us how big to make the background
        plus_size = int(grid.Float_Grid_To_Scr((GRID_SIZE[0] + border_size, 1))[0])

        self.ui.background = pygame.transform.smoothscale(img, (plus_size, plus_size))

        self.input_areas = [
            (self.controls_rect, self.ui.Control_Mouse_Down, self.ui.Control_Mouse_Move),
            (self.game_screen_rect, self.ui.Game_Mouse_Down, self.ui.Game_Mouse_Move) ]

        self.ui.Update_All()

    def Special_Refresh(self) -> None:
        height = self.screen.get_rect().height

        draw_effects.Tile_Texture(self.screen, Images.rivets,
                pygame.Rect(self.menu_margin, 0,
                    self.menu_width, height))

        edge = pygame.Rect(self.menu_margin, - self.margin,
            self.menu_width + self.margin, height + self.margin)

        r: RectType
        for r in [ self.stats_rect, self.global_stats_rect, edge ]:
            draw_effects.Line_Edging(self.screen, r, False)

        r = self.scaled_header_picture.get_rect()
        r.center = self.picture_surf.get_rect().center
        draw_effects.Line_Edging(self.picture_surf, r, False)
        self.picture_surf.blit(self.scaled_header_picture, r.topleft)

    def Special_Action(self, name: str) -> None:
        if name == "ADVANCE":
            New_Mail("SEASON ADVANCE CHEAT")
            self.g.season_ends = 0

        else:
            assert name == "SCREENSHOT"
            pygame.image.save(pygame.display.get_surface(),
                              os.path.join("tmp", "sshot-%04d-%04d.png" % (
                                        self.g.game_time.Get_Day(), self.screen.get_rect().height)))
            New_Mail("SCREENSHOT CHEAT")

    def Main_Loop(self) -> bool:
        alarm_sound = sound.Persisting_Sound(Sounds.emergency)
        g = self.g

        # menu setup
        exit_options: List[MenuItem] = [
            (MenuCommand.MENU, "Exit to Main Menu", [ pygame.K_q ]),
            (MenuCommand.QUIT, "Exit Game", [ pygame.K_F10 ])]

        save_available: List[MenuItem] = [
            (MenuCommand.SAVE, "Save Game", [pygame.K_s]),
            (MenuCommand.LOAD, "Restore Game", [pygame.K_r]),
            (None, None, [])]

        if ( g.challenge == MenuCommand.TUTORIAL ):
            save_available = []

        in_game_menu: menu.Menu = menu.Toggle_Sound_Menu(typing.cast(List[MenuItem], [
            (None, None, []),
            menu.TOGGLE_SOUND,
            (None, None, [])]) +
            save_available + [
            (MenuCommand.HIDE, "Return to Game", [pygame.K_ESCAPE])] +
            exit_options)

        current_menu = in_game_menu

        flash = True
        loop_running = True
        quit = False
        stats_review = False
        in_game_menu.Select(None)
        has_input_focus = True

        # These are for testing (forcing video resize event)
        test_resize_trigger = 0
        test_resize_period = g.challenge.value

        # Almost ready to start... but are we starting
        # from a savegame?
        if ( self.restore_pos is not None ):
            g.challenge = MenuCommand.INTERMEDIATE
            g = self.Restore(self.restore_pos)
            assert g.challenge is not None
        else:
            assert g.challenge is not None
            self.Summary()


        if ( g.challenge == MenuCommand.TUTORIAL ):
            tutor.On()

        cur_time = g.game_time.time()

        # Main loop
        while ( loop_running ):

            menu_open = self.ui.Is_Menu_Open() or (not g.game_running)
            paused = menu_open or (not has_input_focus)
            

            if self.ui.Is_Fast_Forward():
                self.clock.tick(FRAME_RATE * 10)
            elif (self.playback_mode in (PlayMode.PLAYBACK, PlayMode.PLAYTHRU)):
                self.clock.tick(0)
            else:
                self.clock.tick(FRAME_RATE)

            if not paused:
                flash = not flash
                g.game_time.Advance(RT_FRAME_LENGTH)
                draw_obj.Next_Frame() # Flashing lights on the various items

            cur_time = g.game_time.time()
            mail.Set_Day(g.game_time.Get_Day())

            if not paused:
                self.demo.timestamp(g)

            self.ui.Draw_Game(self.game_screen_surf, g.season_fx, paused)

            until_next: List[StatTuple]
            if ( g.challenge == MenuCommand.TUTORIAL ):
                until_next = []
            elif ( g.challenge == MenuCommand.PEACEFUL ):
                until_next = [ ((128,128,128), 12, "Peaceful mode") ]
            else:
                until_next = [ ((128,128,128), 12, "(%d days until next season)" %
                            (( g.season_ends - cur_time ) + 1 )) ]

            self.ui.Draw_Stats(self.stats_surf, typing.cast(List[StatTuple], [
                  ((128,0,128), 18, "Day %u" % g.game_time.Get_Day()),
                  ((128,128,0), 18, g.season_fx.name + " season") ]) +
                  until_next +
                    g.season_fx.Get_Extra_Info())
            self.ui.Draw_Controls(self.controls_surf)

            stats_back = (0,0,0)
            supply = g.net.hub.Get_Steam_Supply()
            demand = g.net.hub.Get_Steam_Demand()
            if ( g.net.hub.Get_Pressure() < PRESSURE_DANGER ):
                # You'll lose the game if you stay in this zone
                # for longer than a timeout. Also, an
                # alarm will sound.

                if ( g.game_ends_at is None ):
                    sound.FX(Sounds.steamcrit)
                    g.warning_given = True

                    New_Mail("Danger! The City needs more steam!", (255,0,0))
                    g.game_ends_at = cur_time + DIFFICULTY.GRACE_TIME
                    assert g.game_ends_at is not None
                    New_Mail("Game will end on Day %u unless supplies are increased." % (
                        int(g.game_ends_at) ), (255,0,0))

                if ( flash ):
                    demand_colour = (255, 0, 0)
                    if not paused:  # NO-COV
                        alarm_sound.Set(0.6)
                else:
                    demand_colour = (128, 0, 0)
                    stats_back = (100, 0, 0)

            elif ( g.net.hub.Get_Pressure() < PRESSURE_WARNING ):

                g.game_ends_at = None
                if ( flash ):
                    demand_colour = (255, 100, 0)
                    if not paused:  # NO-COV
                        alarm_sound.Set(0.3)
                else:
                    demand_colour = (128, 50, 0)
                    stats_back = (50, 25, 0)
            else:

                if ( g.warning_given ):
                    sound.FX(Sounds.steamres)
                    g.warning_given = False

                if ( g.net.hub.Get_Pressure() < PRESSURE_OK ):
                    demand_colour = (128, 128, 0)
                else:
                    demand_colour = (0, 128, 0)

                g.game_ends_at = None
                alarm_sound.Set(0.0)

            avw = g.net.hub.Get_Avail_Work_Units()
            wu_unused = avw - g.work_units_used
            self.global_stats_surf.fill(stats_back)
            stats.Draw_Stats_Window(self.global_stats_surf, [
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

            tutor.Draw(self.screen, g)

            if menu_open:
                current_menu.Draw(self.screen)
                alarm_sound.Set(0.0)

            mail.Draw_Mail(self.game_screen_surf)
            pygame.display.flip()
            mail.Undraw_Mail(self.game_screen_surf)

            if not paused:
                g.season_fx.Per_Frame(RT_FRAME_LENGTH)
                self.ui.Frame_Advance(RT_FRAME_LENGTH)

            # Timing effects
            if ( g.work_timer <= cur_time ):
                # Fixed periodic effects
                g.work_timer = cur_time + 0.1
                g.wu_integral += wu_unused
                g.work_units_used = g.net.Work_Pulse(g.net.hub.Get_Avail_Work_Units())

                g.net.Steam_Think()
                g.net.Expire_Popups()
                mail.Expire_Messages()
                tutor.Examine_Game(g)

            if ( g.season_effect <= cur_time ):
                # Seasonal periodic effects
                g.season_effect = cur_time + g.season_fx.Get_Period()
                g.season_fx.Per_Period()

            if ((( not tutor.Permit_Season_Change() ) and ( g.season == Season.QUIET ))
            or ( g.challenge == MenuCommand.PEACEFUL )):
                # Never-ending season
                g.season_ends = cur_time + 2.0

            elif ( g.season_ends <= cur_time ):
                # Season change
                if (( g.season == Season.QUIET )
                or ( g.season == Season.STORM )):
                    g.season = Season.ALIEN
                    g.season_fx = alien_invasion.Alien_Season(g.net, g.difficulty_level)
                    sound.FX(Sounds.aliensappr)
                elif ( g.season == Season.ALIEN ):
                    g.season = Season.QUAKE
                    g.season_fx = Quake_Season(g.net, g.difficulty_level)
                    if ( not tutor.Active() ): # hack...
                        sound.FX(Sounds.quakewarn)
                elif ( g.season == Season.QUAKE ):
                    g.season = Season.STORM
                    g.season_fx = Storm_Season(g.net, g.difficulty_level)
                    g.difficulty_level *= 1.2 # 20% harder..
                    sound.FX(Sounds.stormwarn)
                else:
                    assert g.season == Season.START
                    g.season = Season.QUIET
                    g.season_fx = Quiet_Season(g.net)

                g.season_ends = cur_time + LENGTH_OF_SEASON
                g.season_effect = cur_time + ( g.season_fx.Get_Period() / 2 )

                # can't ever be PEACEFUL as seasons never end in peaceful mode
                assert g.challenge != MenuCommand.PEACEFUL
                New_Mail("The " + g.season_fx.name +
                         " season has started.", (200,200,200))

            just_ended = False
            if (( g.game_ends_at is not None )
            and ( g.game_ends_at <= cur_time )
            and ( g.game_running )):
                # Game over - you lose
                New_Mail("The City ran out of steam.", (255,0,0))
                New_Mail("Game Over!", (255,255,0))
                sound.FX(Sounds.krankor)
                just_ended = True

            elif (( g.net.hub.tech_level >= DIFFICULTY.CITY_MAX_TECH_LEVEL )
            and ( g.game_running )):
                # Game over - you win!
                g.win = True
                New_Mail("The City is now fully upgraded!", (255,255,255))
                New_Mail("You have won the game!", (255,255,255))
                sound.FX(Sounds.applause)
                just_ended = True

            if ( just_ended ):
                # Won or lost
                current_menu = in_game_menu = menu.Menu(typing.cast(List[MenuItem], [
                    (None, None, []),
                    (MenuCommand.REVIEW, "Review Statistics", [pygame.K_r])]) +
                    exit_options)
                in_game_menu.Select(None)

                # final record from the game:
                g.game_running = False
                g.historian.append(review.Analyse_Network(g))

            if not paused:
                self.demo.do_user_actions(self.ui, self)

            # Events
            if paused:
                e = self.event.wait()
            else:
                e = self.event.poll()

            while ( e.type != pygame.NOEVENT ):
                if e.type == pygame.QUIT:
                    loop_running = False
                    quit = True

                elif e.type == pygame.VIDEORESIZE:
                    self.Recreate_UI()

                elif self.playback_mode in (PlayMode.PLAYBACK, PlayMode.PLAYTHRU):
                    pass

                elif e.type == pygame.ACTIVEEVENT:
                    # Game pauses when input focus is lost
                    if e.state == compatibility.APPINPUTFOCUS:  # NO-COV
                        has_input_focus = (e.gain != 0)

                elif (( e.type == pygame.MOUSEBUTTONDOWN )
                or ( e.type == pygame.MOUSEMOTION )):
                    if (( e.type == pygame.MOUSEBUTTONDOWN )
                    and ( e.button != 1 )):
                        if not menu_open:
                            self.ui.Right_Mouse_Down()

                    elif not menu_open:
                        for (rect, click, move) in self.input_areas:
                            if ( rect.collidepoint(e.pos)):
                                (x,y) = e.pos
                                x -= rect.left
                                y -= rect.top
                                if ( e.type == pygame.MOUSEMOTION ):
                                    move((x,y))
                                else:
                                    click((x,y))
                    else:
                        if ( e.type == pygame.MOUSEMOTION ):
                            current_menu.Mouse_Move(e.pos)
                        else:
                            current_menu.Mouse_Down(e.pos)

                elif e.type == pygame.MOUSEBUTTONUP:
                    self.ui.Cancel_Fast_Forward()

                elif e.type == pygame.KEYDOWN:
                    if not menu_open:
                        self.ui.Key_Press(e.key)

                    else:
                        current_menu.Key_Press(e.key)

                    if ( self.event.is_testing ):  # NO-COV
                        # Cheats.
                        if ( e.key == pygame.K_F10 ):
                            self.demo.Special_Action("ADVANCE", self)
                        elif ( e.key == pygame.K_F9 ):
                            self.screen.fill((255,255,255))
                        elif ( e.key == pygame.K_F8 ):
                            # Lose the game cheat
                            # Heh, worst cheat ever.
                            New_Mail("GAME END CHEAT (LOSE)")
                            g.game_ends_at = 0.0
                            g.net.Lose()
                        elif ( e.key == pygame.K_F7 ):
                            # Place screenshot marker in recording
                            self.demo.Special_Action("SCREENSHOT", self)
                        elif ( e.key == pygame.K_F6 ):
                            # Immediate win
                            New_Mail("GAME END CHEAT (WIN)")
                            g.net.hub.tech_level = DIFFICULTY.CITY_MAX_TECH_LEVEL

                e = self.event.poll()

            # Any commands from the menu?
            if menu_open:
                cmd = current_menu.Get_Command()
                current_menu.Select(None) # consume command

                if ( current_menu == in_game_menu ):

                    # It's the normal menu.
                    if ( cmd == MenuCommand.QUIT ):
                        loop_running = False
                        quit = True
                        self.ui.Reset() # makes menu disappear

                    elif ( cmd == MenuCommand.MENU ):
                        loop_running = False
                        self.ui.Reset()

                    elif ( cmd == MenuCommand.SAVE ):
                        # Switch to alternate menu
                        current_menu = save_menu.Save_Menu(True)

                    elif ( cmd == MenuCommand.LOAD ):
                        current_menu = save_menu.Save_Menu(False)

                    elif ( cmd == MenuCommand.REVIEW ):
                        loop_running = False
                        stats_review = True
                        self.ui.Reset()

                    elif ( cmd is not None ):
                        # Default option - back to game
                        self.ui.Reset()

                else:
                    # It's another menu! That means it's the save menu.
                    assert isinstance(current_menu, save_menu.Save_Menu)
                    if (( cmd is not None )
                    and ( cmd != MenuCommand.UNUSED )
                    and ( cmd != MenuCommand.CANCEL )):
                        if ( not current_menu.Is_Saving() ):
                            g = self.Restore(cmd)

                        else:
                            label = "Day %u - %s season - %s" % (g.game_time.Get_Day(),
                                    g.season_fx.name, time.asctime())

                            result = save_game.Save(g, cmd, label)
                            if ( result is None ):      # NO-COV
                                New_Mail("Game saved.")
                            else:
                                New_Mail(result)        # NO-COV

                    if ( cmd is not None ):
                        # Back to game.
                        self.Special_Refresh()
                        current_menu = in_game_menu
                        self.ui.Reset()

            if (( g.historian_time <= cur_time )
            and ( not paused )):
                g.historian.append(review.Analyse_Network(g))
                g.historian_time = cur_time + 4

            if self.playback_mode == PlayMode.PLAYBACK:
                test_resize_trigger += 1
                if test_resize_trigger >= test_resize_period:
                    test_resize_trigger = 0
                    test_resize_period += test_resize_period // 8
                    self.Recreate_UI()

        tutor.Off()

        # About to exit. Blackout.
        self.screen.fill((0,0,0))
        pygame.display.flip()

        if ( stats_review ):
            review.Review(g, g.historian, self.event)

        return quit

    def Summary(self) -> None:
        g = self.g
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


    def Restore(self, cmd: MenuCommand) -> Game_Data:
        g = self.g
        (g2, result) = save_game.Load(g, cmd)
        if ( result is None ) and ( g2 is not None ):
            self.g = g = g2
            self.ui.net = g.net
            mail.Initialise()
            mail.Set_Day(g.game_time.Get_Day())
            assert g.challenge is not None
            DIFFICULTY.Set(g.challenge)
            New_Mail("Game restored. It is the " +
                g.season_fx.name + " season.")
            self.Summary()
        else:
            assert result is not None
            New_Mail(result)
        return self.g


