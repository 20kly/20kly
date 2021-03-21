#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#
#
# Game statistics review.. no RTS game would be complete without one!
#

import pygame, sys, math, time, pickle


from . import draw_effects, resource, font, menu, game, events
from .primitives import *
from .game_types import *

class Historical_Record:
    def __init__(self, g: "game.Game_Data") -> None:
        self.day = g.game_time.Get_Day()
        self.supply = g.net.hub.Get_Steam_Supply()
        self.demand = g.net.hub.Get_Steam_Demand()
        self.num_nodes = len(g.net.node_list)
        self.num_pipes = len([ p for p in g.net.pipe_list if not p.Is_Destroyed() ])
        self.tech_level = g.net.hub.tech_level
        self.work_units_used = g.work_units_used
        self.work_units_avail = g.net.hub.Get_Avail_Work_Units()
        self.city_pressure = g.net.hub.Get_Pressure()

# Called periodically during the game. Results are appended to a list
# called historian, which is given to the Review function
def Analyse_Network(game_object: "game.Game_Data") -> Historical_Record:
    return Historical_Record(game_object)

# Called at the end of the game, to display statistics:
def Review(game_object: "game.Game_Data",
        historian: List[Historical_Record],
        event: events.Events) -> None:

    available_graphs = [
        ( "Steam Supply", "supply", (0,255,0) ),
        ( "Steam Demand", "demand", (255,0,0) ),
        ( "Number of Nodes", "num_nodes", (128,128,0) ),
        ( "Number of Pipes", "num_pipes", (0,128,0) ),
        ( "City Technology Level", "tech_level", (255,255,0) ),
        ( "Work Unit Usage", "work_units_used", (255,0,255) ),
        ( "Work Unit Availability", "work_units_avail", (0,255,255) ),
        ( "City Steam Pressure", "city_pressure", (0,0,255) ) ]

    def Regraph(arg: Tuple[str, str, Colour]) -> SurfaceType:
        screen = event.resurface()
        (width, height) = screen.get_rect().size
        g = game_object
        draw_effects.Tile_Texture(screen, Images.i006metal, screen.get_rect())

        def Text(text: str, size: int,
                 xy: SurfacePosition, justify: int) -> int:
            (x,y) = xy
            img = font.Get_Font(size).render(text, True, (255, 255, 255))

            if ( justify == 0 ): # centre
                x -= ( img.get_rect().width ) // 2
            elif ( justify < 0 ): # right
                x -= img.get_rect().width

            screen.blit(img, (x,y))
            y += img.get_rect().height
            return y + 5


        if ( g.win ):
            y = Text("You have won the game!", 36, (width // 2, 10), 0)
        else:
            y = Text("You have lost the game!", 36, (width // 2, 10), 0)

        Text("Thankyou for playing!", 15, (width // 2, y), 0)

        y += height // 10

        lev = dict()
        lev[ MenuCommand.TUTORIAL ] = lev[ MenuCommand.BEGINNER ] = "Beginner"
        lev[ MenuCommand.INTERMEDIATE ] = "Intermediate"
        lev[ MenuCommand.EXPERT ] = "Expert"
        lev[ MenuCommand.PEACEFUL ] = "Peaceful"
        level = lev.get(g.challenge, "??")

        score = float(g.net.hub.total_steam) / max(1.0, float(g.game_time.Get_Day()))
        if ( g.win ):
            score *= 8

        score = int(score)

        l = [ ( "Game length", "%u days" % g.game_time.Get_Day() ),
            ( "Steam used", "%1.1f U" % g.net.hub.total_steam ),
            ( "Unused work units", "%u" % g.wu_integral ),
            ( "Game level", level ),
            ( "Your " + level + " Score", "%u" % score ) ]

        r: RectType = pygame.Rect(25, y, width // 2, 1)
        y = Text("Summary", 18, r.center, 0)

        for (key, data) in l:
            Text(key, 18, (r.left, y), 1)
            y = Text(data , 18, (r.right, y), -1)

        r.height = y - r.top
        r = r.inflate(10,10)
        pygame.draw.rect(screen, (128, 128, 128), r, 2)

        y = r.bottom + ( height // 10 )

        graph_window = pygame.Rect(r.left, y, r.width, ( height - y ) - 25 )


        (heading, attribute, colour) = arg
        pygame.draw.rect(screen, (0, 0, 0), graph_window)
        pygame.draw.rect(screen, (128, 128, 128), graph_window, 2)

        graph_subwin = graph_window.inflate(-25,-25)
        (x,y) = graph_subwin.center
        y = graph_window.top + 5
        Text(heading, 18, (x,y), 0)

        text_margin = 30

        graph_subwin.height -= text_margin
        graph_subwin.top += text_margin

        assert len(historian) != 0

        max_gt = max_gy = 1
        values = []
        for hr in historian:
            try:
                gy = getattr(hr, attribute)
            except AttributeError:  # NO-COV
                print("Attribute",attribute,"not present")
                return screen

            if ( gy < 0 ):  # NO-COV
                gy = 0 # This should not happen
            gt = hr.day

            values.append((gt, gy))

            max_gt = max(int(math.ceil(gt)), max_gt)
            max_gy = max(int(math.ceil(gy)), max_gy)

        def Calc_Step_Max(maximum: float,
                          number_of_steps: float) -> Tuple[int, int]:
            step = int((float(maximum) / float(number_of_steps)) + 1)
            if ( step < 1 ):  # NO-COV
                step = 1

            return (step, int( step * number_of_steps ))

        (step_gt, max_gt) = Calc_Step_Max(max_gt, 20)
        (step_gy, max_gy) = Calc_Step_Max(max_gy, 10)

        t_scale = float(graph_subwin.width) / float(max_gt)
        y_scale = -1.0 * ( float(graph_subwin.height) / float(max_gy) )

        # Vertical divisions
        for gt in range(0, max_gt, step_gt):
            x = int( gt * t_scale ) + graph_subwin.left
            pygame.draw.line(screen, (55,55,55),
                    (x, graph_subwin.bottom),
                    (x, graph_subwin.top))
            pygame.draw.line(screen, (255,255,255),
                    (x, graph_subwin.bottom),
                    (x, graph_subwin.bottom - 2))

        # Horizontal divisions
        for gy in range(0, max_gy, step_gy):
            y = int( gy * y_scale ) + graph_subwin.bottom
            pygame.draw.line(screen, (75,75,75),
                    (graph_subwin.left, y),
                    (graph_subwin.right, y))
            pygame.draw.line(screen, (75,75,75),
                    (graph_subwin.left, y),
                    (graph_subwin.left + 2, y))


        # Graph line
        (x1,y1) = graph_subwin.bottomleft
        for (gt, gy) in values:
            x = int( gt * t_scale ) + graph_subwin.left
            y = int( gy * y_scale ) + graph_subwin.bottom
            pygame.draw.line(screen, colour, (x1, y1), (x,y))
            (x1, y1) = (x, y)

        # Graph border
        pygame.draw.line(screen, (255,255,255),
                graph_subwin.topleft, graph_subwin.bottomleft)
        pygame.draw.line(screen, (255,255,255),
                graph_subwin.bottomright, graph_subwin.bottomleft)

        return screen


    screen = Regraph(available_graphs[ 0 ])
    graph_num = 0

    # then...

    proceed = menu.Menu(
                [(None, None, []),
                (MenuCommand.PREV, "Previous Graph", [pygame.K_LEFT]),
                (MenuCommand.NEXT, "Next Graph", [pygame.K_RIGHT]),
                (None, None, []),
                (MenuCommand.MENU, "Continue", [ pygame.K_ESCAPE ])])

    quit = False
    while ( not quit ):
        screen = Regraph(available_graphs[ graph_num ])
        (width, height) = screen.get_rect().size

        (quit, cmd) = menu.Simple_Menu_Loop(screen,
                    proceed, (( width * 3 ) // 4, height // 2 ), event)

        if ( cmd == MenuCommand.MENU ):
            quit = True
        elif ( cmd == MenuCommand.PREV ):
            graph_num = (( graph_num + len(available_graphs) - 1 )
                                % len(available_graphs))
        elif ( cmd == MenuCommand.NEXT ):
            graph_num = ( graph_num + 1 ) % len(available_graphs)

    return


