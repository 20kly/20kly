#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import game_random, map_items, network, grid, quiet_season
from .ui import User_Interface
from .primitives import *
from .game_types import *
from .unit_test import *


def test_UI() -> None:
    """Unit tests for the ui.py module.

    This is the game's user interface: the screen shows the map, the user can click
    things. These unit tests carry out various test scenarios by interacting with
    the ui using Game_Mouse_Down and others. There is some overlap with the unit
    tests of network.py which also involve creating/removing nodes and pipes; the
    difference is the API used to drive the tests, which is provided by ui.py in this
    case."""

    # create test scenario
    test_screen = Setup_For_Unit_Test()
    demo = game_random.Game_Random(1)
    net = network.Network(demo, False)
    ui = User_Interface(net, demo, RESOLUTION)
    controls_surf = pygame.Surface((200, 200))

    season_fx = quiet_season.Quiet_Season(net)

    def Draw_Things(shaking: bool) -> None:
        class Test_Season(quiet_season.Quiet_Season):
            def Is_Shaking(self) -> bool:
                return shaking

        ui.Draw_Game(test_screen, Test_Season(net))
        ui.Draw_Stats(test_screen, [])
        pygame.display.flip()

    Draw_Things(False)

    # Initially the control_menu field is None, so all of these
    # input events are not routed to the control menu
    ui.Game_Mouse_Move((10, 10))
    ui.Key_Press(pygame.K_1)
    ui.Control_Mouse_Move((10, 10))
    ui.Control_Mouse_Down((10, 10))
    ui.Reset()
    Draw_Things(False)

    # Now we create the control menu by drawing it for the first time
    ui.Draw_Controls(controls_surf)

    # Now the control menu can receive events
    ui.Game_Mouse_Move((10, 10))
    ui.Key_Press(pygame.K_1)
    ui.Control_Mouse_Move((10, 10))
    ui.Control_Mouse_Down((10, 10))
    ui.Reset()
    Draw_Things(False)

    # Let us make some nodes
    # Here is a map showing where the nodes are placed (not to scale):
    #
    #    n1      n2
    #
    #    n4      n3
    #
    n1pos = (100, 100)
    n2pos = (200, 100)
    n3pos = (200, 200)
    n4pos = (100, 200)
    p12pos = (150, 100)
    missed = (250, 250)

    ui.Key_Press(pygame.K_n)        # build node (n1pos)
    ui.Game_Mouse_Move(n1pos)
    Draw_Things(False)              # draw pipe under construction
    ui.Game_Mouse_Down(n1pos)
    ui.Key_Press(pygame.K_n)        # build node (n2pos)
    ui.Game_Mouse_Down(n2pos)
    ui.Key_Press(pygame.K_p)        # build pipe from 2 to 1
    ui.Game_Mouse_Move(n1pos)
    Draw_Things(False)              # draw pipe under construction
    ui.Game_Mouse_Down(n1pos)
    ui.Key_Press(pygame.K_n)        # build node (n3pos)
    ui.Game_Mouse_Down(n3pos)
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_p)
    ui.Game_Mouse_Down(n3pos)       # create pipe from 3 to 1
    ui.Game_Mouse_Down(n1pos)       # create pipe from 3 to 1
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Game_Mouse_Move(missed)
    Draw_Things(False)              # draw with nothing selected
    ui.Game_Mouse_Down(p12pos)      # click on pipe from 2 to 1 (select it)
    ui.Game_Mouse_Down(p12pos)      # click again (already selected)
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_u)
    ui.Game_Mouse_Down(p12pos)      # upgrade pipe from 2 to 1
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_d)
    ui.Game_Mouse_Down(p12pos)      # destroy pipe from 2 to 1
    ui.Key_Press(pygame.K_d)
    ui.Game_Mouse_Down(missed)      # destroy nothing (missed!)
    ui.Key_Press(pygame.K_d)
    ui.Game_Mouse_Down(n1pos)       # destroy node 1
    ui.Right_Mouse_Down()           # neutral mode
    ui.Game_Mouse_Down(n3pos)       # select node 3
    ui.Key_Press(pygame.K_u)
    ui.Game_Mouse_Down(missed)      # upgrade nothing (missed)
    ui.Key_Press(pygame.K_u)
    ui.Game_Mouse_Down(n2pos)       # upgrade node 2
    ui.Right_Mouse_Down()           # neutral mode
    ui.Game_Mouse_Down(n3pos)       # select node 3
    ui.Key_Press(pygame.K_u)        # upgrade node 3
    ui.Key_Press(pygame.K_d)        # destroy node 3
    Draw_Things(False)

    # Make sure we have a well
    w = map_items.Well(grid.Scr_To_Grid(n4pos))
    net.Add_Grid_Item(w, True)
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_p)        # pipe mode
    ui.Game_Mouse_Down(n4pos)       # click on the well (nothing happens)
    ui.Key_Press(pygame.K_n)        # build node over the well
    ui.Game_Mouse_Down(n4pos)

    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_p)        # try to build a pipe from a node to itself
    ui.Game_Mouse_Down(n2pos)
    ui.Game_Mouse_Down(n2pos)

    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_p)        # build a pipe from 2 to 4
    ui.Game_Mouse_Down(n2pos)
    ui.Game_Mouse_Down(n4pos)
    
    ui.Key_Press(pygame.K_n)        # build node (n1pos)
    ui.Game_Mouse_Down(n1pos)
    ui.Key_Press(pygame.K_n)        # build node (n3pos)
    ui.Game_Mouse_Down(n3pos)
    Draw_Things(False)

    # Now we can't build a pipe from 1 to 3 because it crosses the pipe from 2 to 4
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Key_Press(pygame.K_p)        # build a pipe from 1 to 3 (doesn't work)
    ui.Game_Mouse_Down(n1pos)
    ui.Game_Mouse_Down(n3pos)

    # Select node 4 and then destroy it without informing the ui
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Game_Mouse_Down(n4pos)
    n4 = ui.selection
    assert n4 is not None
    net.Destroy(n4)
    assert ui.selection == n4
    ui.Game_Mouse_Down(n4pos)       # select it again - outcome: nothing selected
    assert ui.selection is None

    # Test the control menu with mouse clicks
    centre_of: Dict[MenuCommand, SurfacePosition] = dict()
    for (cmd, rect) in ui.control_menu.control_rects:
        (x, y) = rect.center
        x += ui.control_menu.bbox.left
        y += ui.control_menu.bbox.top
        centre_of[cmd] = (x, y)

    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Control_Mouse_Down(centre_of[MenuCommand.UPGRADE]) # upgrade nothing
    ui.Right_Mouse_Down()           # neutral mode (deselect all)
    ui.Game_Mouse_Down(n3pos)       # select n3
    assert ui.selection is not None
    ui.Control_Mouse_Down(centre_of[MenuCommand.UPGRADE]) # upgrade n3
    ui.Game_Mouse_Down(n3pos)       # select n3
    ui.Control_Mouse_Down(centre_of[MenuCommand.BUILD_NODE]) # build nothing (n3 selected)
    ui.Control_Mouse_Down(centre_of[MenuCommand.DESTROY]) # destroy n3
    Draw_Things(False)

    # Select the city (testing Draw_Stats)
    ui.Game_Mouse_Down(grid.Grid_To_Scr(net.hub.pos))
    Draw_Things(False)

    # Earthquake!
    Draw_Things(True)

