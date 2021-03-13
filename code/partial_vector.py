#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

from .game_types import *

# The function returns (x,y), a point on the line between
# (x1,y1) and (x2,y2), such that a / b of the line
# is between (x,y) and (x1,y1).

def Partial_Vector(arg1: FloatSurfacePosition, arg2: FloatSurfacePosition,
                   arg3: Tuple[float, float]) -> FloatSurfacePosition:
    (x1,y1) = arg1
    (x2,y2) = arg2
    (a,b) = arg3
    x = x1 + ((( x2 - x1 ) * a ) / b )
    y = y1 + ((( y2 - y1 ) * a ) / b )
    return (x,y)

