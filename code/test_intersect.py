#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import random, math

from .intersect import Intersect, Intersect_Grid_Square
from .game_types import *


def test_Intersect() -> None:

    r = random.Random(1)

    def BT(xp, line1, line2):
        assert Intersect(line1, line2) == xp
        assert Intersect(line2, line1) == xp

    def Rnd() -> None:
        def RP():
            return (r.random(), r.random())

        (x,y) = RP() # choose intersection point.
        (xa1,ya1) = RP() # line 1 source
        (xb1,yb1) = RP() # line 2 source

        aang = math.atan2( y - ya1 , x - xa1 ) # line 1 angle
        bang = math.atan2( y - yb1 , x - xb1 ) # line 2 angle

        xa2 = xa1 + ( math.cos(aang) * 10.0 )
        xb2 = xb1 + ( math.cos(bang) * 10.0 )
        ya2 = ya1 + ( math.sin(aang) * 10.0 )
        yb2 = yb1 + ( math.sin(bang) * 10.0 )

        z = Intersect(((xa1,ya1),(xa2,ya2)),((xb1,yb1),(xb2,yb2)))
        assert z is not None
        (xi, yi) = z
        assert math.hypot(xi - x, yi - y) < 0.0001

    BT((3,2),((3,1),(3,5)),((2,2),(4,2)))   # cross
    BT(None,((3,1),(3,5)),((1,1),(1,5)))    # parallel lines
    BT((2,2),((1,1),(3,3)),((1,3),(3,1)))   # X
    BT(None,((1,1),(3,3)),((2,2),(4,4)))    # parallel lines, on top of each other

    for i in range(10000):
        Rnd()

def test_Intersect_Grid_Square() -> None:
    surround = [(-1, -1), (0, -1), (1, -1),
                (1, 0), (1, 1), (0, 1),
                (-1, 1), (-1, 0)]

    # Line straight through the middle of the square - intersects
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 4) % 8]
        assert Intersect_Grid_Square((0, 0), (outside1, outside2))

    # Line through the square, not the middle - intersects
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 3) % 8]
        assert Intersect_Grid_Square((0, 0), (outside1, outside2))

    # Line touching the corners of the square
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 2) % 8]
        assert not Intersect_Grid_Square((0, 0), (outside1, outside2))

    # Line past the square
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 1) % 8]
        assert not Intersect_Grid_Square((0, 0), (outside1, outside2))

    # Line to the middle of the square - doesn't intersect
    for i in range(8):
        outside = surround[i]
        assert not Intersect_Grid_Square((0, 0), (outside, (0, 0)))
        assert not Intersect_Grid_Square((0, 0), ((0, 0), outside))


