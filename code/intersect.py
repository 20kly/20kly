#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


from game_types import *

# Line intersection algorithm. Thanks to page 113 of
# Computer Graphics Principles and Practice (2nd. Ed), Foley et al.
#
# Note 1: it's not an intersection if the two lines share an endpoint.
# Note 2: Can't detect overlapping parallel lines.

def Intersect(arg1: Tuple[FloatGridPosition, FloatGridPosition],
              arg2: Tuple[FloatGridPosition, FloatGridPosition]) -> Optional[FloatGridPosition]:
    ((xa1,ya1),(xa2,ya2)) = arg1
    ((xb1,yb1),(xb2,yb2)) = arg2
    xa = xa2 - xa1
    ya = ya2 - ya1
    xb = xb2 - xb1
    yb = yb2 - yb1

    a = ( xa * yb ) - ( xb * ya )
    if ( a == 0 ):
        return None

    b = ((( xa * ya1 ) + ( xb1 * ya ) - ( xa1 * ya )) - ( xa * yb1 ))
    tb = float(b) / float(a)

    if (( tb <= 0 ) or ( tb >= 1 )):
        return None # doesn't intersect

    if ( xa == 0 ):
        if ( ya == 0 ):
            return None # you've confused a line with a point.
        ta = ( yb1 + ( yb * tb ) - ya1 ) / float(ya)
    else:
        ta = ( xb1 + ( xb * tb ) - xa1 ) / float(xa)

    if (( ta <= 0 ) or ( ta >= 1 )):
        return None # doesn't intersect

    x = xb1 + ( xb * tb )
    y = yb1 + ( yb * tb )
    return (x,y)



def test_Intersect() -> None:
    import random, math

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
