#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import game_random, map_items, network, unit_test
from .ui import User_Interface
from .primitives import *
from .game_types import *


def Do_Building_Test(building: map_items.Building,
                     cannot_be_damaged: bool) -> None:
    test_screen = unit_test.Setup_For_Unit_Test()

    """Test for map_items.py.

    This tests the lifecycle of a building - construction,
    upgrade, destruction. It is used to test every building type.
    The buildings are drawn during testing. Though there are
    some assertions here, Get_Things() is primarily intended
    to produce 100% coverage."""

    building.Exits()
    building.Sound_Effect()

    def Get_Things() -> None:
        building.Get_Information()
        building.Get_Diagram_Colour()
        building.Get_Tech_Level()
        building.Get_Health_Meter()
        building.Get_Popup_Items()
        building.Draw(test_screen)
        building.Draw_Selected(test_screen, (255, 0, 0))
        building.Draw_Popup(test_screen)
        pygame.display.flip()

    # construction
    max_work = 1000
    while building.Needs_Work():
        max_work -= 1
        Get_Things()
        building.Do_Work()
        assert not building.Is_Destroyed()
        assert max_work > 0

    assert not building.Is_Broken()
    assert not building.Is_Destroyed()

    # full health
    Get_Things()

    # upgrading
    building.Begin_Upgrade()
    while building.Needs_Work():
        max_work -= 1
        Get_Things()
        building.Do_Work()
        assert not building.Is_Destroyed()
        assert max_work > 0

    # upgraded
    Get_Things()

    if cannot_be_damaged:
        return

    # minor damage
    building.Take_Damage()
    assert not building.Is_Destroyed()
    assert building.Is_Broken()
    assert building.Needs_Work()

    # repair
    while building.Needs_Work():
        max_work -= 1
        Get_Things()
        building.Do_Work()
        assert not building.Is_Destroyed()
        assert max_work > 0

    assert not building.Is_Broken()

    # major damage
    while not building.Is_Destroyed():
        max_work -= 1
        building.Take_Damage()
        Get_Things()
        assert max_work > 0
        assert building.Is_Broken()

    # it's too late to do any work
    assert building.Is_Destroyed()
    building.Do_Work()

def test_Building() -> None:
    Do_Building_Test(map_items.Building((1, 1), "foobar"), False)

def test_Node() -> None:
    Do_Building_Test(map_items.Node((1, 1)), False)

def test_Well_Node() -> None:
    Do_Building_Test(map_items.Well_Node((1, 1)), False)

def test_City() -> None:
    Do_Building_Test(map_items.City_Node((1, 1)), True)

def test_Pipe() -> None:
    demo = game_random.Game_Random(1)
    net = network.Network(demo, False)
    n1 = map_items.Node((1, 1))
    n2 = map_items.Node((3, 3))
    assert net.Add_Grid_Item(n1)
    assert net.Add_Grid_Item(n2)
    pipe = net.Add_Pipe(n1, n2)
    assert pipe
    Do_Building_Test(pipe, False)

