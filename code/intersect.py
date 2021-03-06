#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


from .game_types import *

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
        # xa and ya can't both be zero - if they are, a == 0 too
        ta = ( yb1 + ( yb * tb ) - ya1 ) / float(ya)
    else:
        ta = ( xb1 + ( xb * tb ) - xa1 ) / float(xa)

    if (( ta <= 0 ) or ( ta >= 1 )):
        return None # doesn't intersect

    x = xb1 + ( xb * tb )
    y = yb1 + ( yb * tb )
    return (x,y)


# Check line (a,b) against given grid pos
def Intersect_Grid_Square(gpos: GridPosition, ab: Tuple[GridPosition, GridPosition]) -> bool:
    (a,b) = ab
    (x1,y1) = gpos
    x = float(x1) - 0.5
    y = float(y1) - 0.5
    for (c,d) in [ ((x,y), (x+1,y+1)), ((x+1,y),(x,y+1)) ]:
        if ( Intersect((a,b), (c,d)) is not None ):
            return True

    return False
