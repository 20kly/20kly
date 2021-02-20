# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 
#
# Game statistics review.. no RTS game would be complete without one!
#

import pygame , sys , math , time , pickle
from pygame.locals import *

import extra , resource , stats , menu
from primitives import *

class Historical_Record:
    pass

# Called periodically during the game. Results are appended to a list
# called historian, which is given to the Review function
def Analyse_Network(game_object):
    hr = Historical_Record()
    g = game_object

    hr.day = g.game_time.Get_Day()
    hr.supply = g.net.hub.Get_Steam_Supply()
    hr.demand = g.net.hub.Get_Steam_Demand()
    hr.num_nodes = len(g.net.node_list)
    hr.num_pipes = len([ p for p in g.net.pipe_list if not p.Is_Destroyed() ])
    hr.tech_level = g.net.hub.tech_level
    hr.work_units_used = g.work_units_used
    hr.work_units_avail = g.net.hub.Get_Avail_Work_Units()
    hr.city_pressure = g.net.hub.Get_Pressure()

    return hr

# Called at the end of the game, to display statistics:
def Review(screen, width_height, game_object, historian):

    (width, height) = width_height
    g = game_object
    extra.Tile_Texture(screen, "006metal.jpg", screen.get_rect())

    def Text(str, size, xy, justify):
        (x,y) = xy
        img = stats.Get_Font(size).render(str, True, (255, 255, 255))

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
    lev[ MENU_TUTORIAL ] = lev[ MENU_BEGINNER ] = "Beginner"
    lev[ MENU_INTERMEDIATE ] = "Intermediate"
    lev[ MENU_EXPERT ] = "Expert"
    lev[ MENU_PEACEFUL ] = "Peaceful"
    if ( not lev.has_key( g.challenge ) ):
        level = "??"
    else:
        level = lev[ g.challenge ]

    score = float(g.net.hub.total_steam) / float(g.game_time.Get_Day())
    if ( g.win ):
        score *= 8

    score = int(score)

    l = [ ( "Game length", "%u days" % g.game_time.Get_Day() ),
        ( "Steam used", "%1.1f U" % g.net.hub.total_steam ),
        ( "Unused work units", "%u" % g.wu_integral ),
        ( "Game level", level ),
        ( "Your " + level + " Score", "%u" % score ) ]

    r = Rect(25, y, width // 2, 1)
    y = Text("Summary", 18, r.center, 0)

    for (key, data) in l:
        Text(key, 18, (r.left, y), 1)
        y = Text(data , 18, (r.right, y), -1)

    r.height = y - r.top
    r = r.inflate(10,10)
    pygame.draw.rect(screen, (128, 128, 128), r, 2)

    y = r.bottom + ( height // 10 )

    graph_window = Rect(r.left, y, r.width, ( height - y ) - 25 )


    available_graphs = [
        ( "Steam Supply", "supply", (0,255,0) ),
        ( "Steam Demand", "demand", (255,0,0) ),
        ( "Number of Nodes", "num_nodes", (128,128,0) ),
        ( "Number of Pipes", "num_pipes", (0,128,0) ),
        ( "City Technology Level", "tech_level", (255,255,0) ),
        ( "Work Unit Usage", "work_units_used", (255,0,255) ),
        ( "Work Unit Availability", "work_units_avail", (0,255,255) ),
        ( "City Steam Pressure", "city_pressure", (0,0,255) ) ]

    def Regraph(arg):
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

        if ( len(historian) == 0 ):
            print("Historian has no data - no graph available")
            return


        max_gt = max_gy = 0
        values = []
        for hr in historian:
            try:
                gy = getattr(hr, attribute)
            except Attribute_Error:
                print("Attribute",attribute,"not present")
                return

            if ( gy < 0 ):
                gy = 0 # This should not happen
            gt = hr.day

            values.append((gt, gy))

            if ( gt > max_gt ):
                max_gt = gt
            if ( gy > max_gy ):
                max_gy = gy

        if (( max_gt <= 0 ) or ( max_gy <= 0 )):
            print("Graph not available (/0)")
            return

        def Calc_Step_Max(maximum,number_of_steps):
            step = int((float(maximum) / float(number_of_steps)) + 1)
            if ( step < 1 ):
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


    Regraph(available_graphs[ 0 ])
    graph_num = 0

    # then...
    
    proceed = menu.Menu( 
                [(None, None, []),
                (MENU_PREV, "Previous Graph", []),
                (MENU_NEXT, "Next Graph", []),
                (None, None, []),
                (MENU_MENU, "Continue", [ K_ESCAPE ])])

    quit = False
    while ( not quit ):
        (quit, cmd) = extra.Simple_Menu_Loop(screen, 
                    proceed, (( width * 3 ) // 4, height // 2 ))

        if ( cmd == MENU_MENU ):
            quit = True
        elif ( cmd == MENU_PREV ):
            graph_num = (( graph_num + len(available_graphs) - 1 )
                                % len(available_graphs))
            Regraph(available_graphs[ graph_num ])
        elif ( cmd == MENU_NEXT ):
            graph_num = ( graph_num + 1 ) % len(available_graphs)
            Regraph(available_graphs[ graph_num ])


    return


