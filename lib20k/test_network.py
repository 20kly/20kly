#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

from . import game_random, map_items, network, unit_test
from .primitives import *
from .game_types import *



def test_Network() -> None:
    """Test for network.py.

    This tests the map, which consists of a 2D grid and also
    a graph of connections between map_items. Checks are
    performed using assertions. We add/remove elements and
    connections between them."""

    test_screen = unit_test.Setup_For_Unit_Test()
    demo = game_random.Game_Random(1)
    net = network.Network(demo, False)

    # check city is connected
    assert net.Is_Connected(net.hub)

    # Try to destroy the city (doesn't work)
    net.Destroy(net.hub)

    # Here is a map showing where the nodes are placed (not to scale)
    #
    # 1,1   n2          n6
    #                 n7  
    #   n4  n3  n5
    #
    #       n1

    # Add a destroyed node (won't work)
    n1 = map_items.Node((5, 5))
    # note: destroy the node before adding it to the map
    max_work = 1000
    while not n1.Is_Destroyed():
        max_work -= 1
        n1.Take_Damage()
        assert max_work > 0
    assert not net.Add_Grid_Item(n1, inhibit_effects=True)
    assert not net.Add_Grid_Item(n1, inhibit_effects=False)

    # Add a node of a weird type (not allowed)
    i1 = map_items.Item((5, 5), "foobar")
    assert not net.Add_Grid_Item(i1)

    # Add a node normally
    n1 = map_items.Node((5, 5))
    assert net.Add_Grid_Item(n1)

    # Add another node at the same position (not allowed)
    i2 = map_items.Node((5, 5))
    assert not net.Add_Grid_Item(i2, inhibit_effects=True)
    assert not net.Add_Grid_Item(i2, inhibit_effects=False)

    # Add another node at another position
    n2 = map_items.Node((5, 1))
    assert net.Add_Grid_Item(n2)

    # Add a pipe between the nodes
    pipe12 = net.Add_Pipe(n1, n2)
    assert pipe12 is not None

    # Can't add another pipe in the same place
    assert net.Add_Pipe(n1, n2) is None

    # Add a node in the middle of the pipe (not allowed)
    n3 = map_items.Node((5, 3))
    assert not net.Add_Grid_Item(n3, inhibit_effects=True)
    assert not net.Add_Grid_Item(n3, inhibit_effects=False)

    # Make sure we can find pipe12
    assert net.Get_Pipe(n1.pos) == pipe12
    assert net.Get_Pipe(n2.pos) == pipe12
    assert net.Get_Pipe((5, 2)) == pipe12
    assert net.Get_Pipe((5, 4)) == pipe12

    # Destroy the pipe and try again
    net.Destroy(pipe12)
    assert net.Add_Grid_Item(n3) # n3 added

    # more nodes
    n4 = map_items.Node((3, 3))
    assert net.Add_Grid_Item(n4)
    n5 = map_items.Node((7, 3))
    assert net.Add_Grid_Item(n5)

    # Can't connect n5 and n4 because there is a node in the way (n3)
    assert net.Add_Pipe(n5, n4) is None

    # destroy n3 (without removing it from the grid)
    while not n3.Is_Destroyed():
        max_work -= 1
        n3.Take_Damage()
        assert max_work > 0

    # connection is possible
    pipe54 = net.Add_Pipe(n5, n4)
    assert pipe54 is not None

    # Can't add pipe12 again - there's a pipe in the way now
    assert net.Add_Pipe(n1, n2) is None

    # Can't add pipe13 either as n3 is destroyed
    assert net.Add_Pipe(n1, n3) is None

    # Pipe64 runs very close to pipe 54 but it's still allowed
    n6 = map_items.Node((10, 1))
    assert net.Add_Grid_Item(n6)
    pipe64 = net.Add_Pipe(n6, n4)
    assert pipe64 is not None

    # pipe25 would not be allowed - pipe64 in the way
    assert net.Add_Pipe(n2, n5) is None

    # can't place a node too close to pipe64 but this location is ok
    # aim is to be in a square that's near to the pipe but not actually blocked by it
    n7 = map_items.Node((9, 2))
    assert net.Add_Grid_Item(n7)

    # Destroy pipe64 and try to add pipe25 again
    net.Destroy(pipe64)

    # immediately after destroying a pipe, Get_Pipe has a slightly different code path
    assert net.Get_Pipe((8, 2)) is None

    pipe25 = net.Add_Pipe(n2, n5)
    assert pipe25 is not None

    # Make sure we can find pipe25
    assert net.Get_Pipe((6, 2)) == pipe25

    # and pipe54
    assert net.Get_Pipe((5, 3)) == pipe54

    # Destroy unconnected node n7
    net.Destroy(n7)



