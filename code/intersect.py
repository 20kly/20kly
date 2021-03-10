#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import math
from .game_types import *

# Line intersection algorithm. Thanks to page 113 of
# Computer Graphics Principles and Practice (2nd. Ed), Foley et al.
#
# Note 1: it's not an intersection if the two lines share an endpoint.
# Note 2: Can't detect overlapping parallel lines.

def Lines_Intersect(arg1: FloatGridLine, arg2: FloatGridLine) -> bool:
    ((xa1, ya1), (xa2, ya2)) = arg1
    ((xb1, yb1), (xb2, yb2)) = arg2
    xa = xa2 - xa1
    ya = ya2 - ya1
    xb = xb2 - xb1
    yb = yb2 - yb1

    a = ( xa * yb ) - ( xb * ya )
    if ( a == 0.0 ):
        return False

    b = ((( xa * ya1 ) + ( xb1 * ya ) - ( xa1 * ya )) - ( xa * yb1 ))
    tb = float(b) / float(a)

    if (( tb <= 0.0 ) or ( tb >= 1.0 )):
        return False # doesn't intersect

    if ( xa == 0.0 ):
        # xa and ya can't both be zero - if they are, a == 0 too
        ta = ( yb1 + ( yb * tb ) - ya1 ) / float(ya)
    else:
        ta = ( xb1 + ( xb * tb ) - xa1 ) / float(xa)

    if (( ta <= 0.0 ) or ( ta >= 1.0 )):
        return False # doesn't intersect

    return True  # intersects at xb1 + ( xb * tb ), yb1 + ( yb * tb )

def Distance_From_Point_To_Line(gpos: FloatGridPosition, ab: GridLine) -> float:
    """Compute the distance from gpos to the nearest point on the line ab"""

    # Based on https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    # "Line defined by two points" 
    (x0, y0) = gpos
    ((x1, y1), (x2, y2)) = ab

    return abs(((x2 - x1) * (y1 - y0)) - ((x1 - x0) * (y2 - y1))) / math.hypot(x2 - x1, y2 - y1)


def Intersects_Node(gpos: FloatGridPosition, ab: GridLine) -> bool:
    """Return true if line ab intersects a node in this grid square."""
    return Distance_From_Point_To_Line(gpos, ab) < 0.5

# When checking for intersection with a grid square, check slightly
# beyond the edges of the square, so as to catch edge cases and corner cases.
# (These are, of course, *literally* edge cases and corner cases.)
EPSILON = 1.0 / 16.0

class GridRect:
    def __init__(self, topleft: GridPosition, bottomright: GridPosition) -> None:
        (self.left, self.top) = topleft
        (self.right, self.bottom) = bottomright
        assert self.left < self.right
        assert self.top < self.bottom
        assert type(self.left) == int
        assert type(self.right) == int
        assert type(self.top) == int
        assert type(self.bottom) == int

    def Subdivide(self, line: FloatGridLine) -> "List[GridRect]":
        """Given a line from pos1 to pos2, subdivide the area in
        this GridRect into between 0 and 4 smaller rectangles, all
        of which include some part of the line."""

        xdiv = (self.left + self.right) // 2
        ydiv = (self.top + self.bottom) // 2

        todo: List[GridRect] = []
        if xdiv > self.left:
            # 2 or 4 rectangles
            if ydiv > self.top:
                # definitely 4 rectangles
                todo.append(GridRect((self.left, self.top), (xdiv, ydiv)))
                todo.append(GridRect((xdiv, self.top), (self.right, ydiv)))

            todo.append(GridRect((self.left, ydiv), (xdiv, self.bottom)))
            todo.append(GridRect((xdiv, ydiv), (self.right, self.bottom)))
        else:
            # 1 or 2 rectangles
            if ydiv > self.top:
                # definitely 2 rectangles
                todo.append(GridRect((self.left, self.top), (self.right, ydiv)))

            todo.append(GridRect((self.left, ydiv), (self.right, self.bottom)))

        # which of the rectangles are intersected by the line?
        keep: List[GridRect] = []
        for rect in todo:
            if rect.Intersects(line):
                keep.append(rect)

        return keep

    def Intersects(self, line: FloatGridLine) -> bool:
        """Return True if line intersects this GridRect."""
        x1 = self.left - 0.5
        x2 = self.right - 0.5
        y1 = self.top - 0.5
        y2 = self.bottom - 0.5
        e = EPSILON
        return (Lines_Intersect(line, ((x1, y1 - e), (x1, y2 + e)))     # left
            or Lines_Intersect(line, ((x2, y1 - e), (x2, y2 + e)))      # right
            or Lines_Intersect(line, ((x1 - e, y1), (x2 + e, y1)))      # top
            or Lines_Intersect(line, ((x1 - e, y2), (x2 + e, y2))))     # bottom

    def IsMinimum(self) -> bool:
        """Return True if this rectangle is as small as it can be (1 grid square)."""
        return ((self.right - self.left) == 1) and ((self.bottom - self.top) == 1)
   
    def Position(self) -> GridPosition:
        """Return a grid position within the rectangle."""
        return (self.left, self.top)

    def RecursiveSubdivide(self, line: FloatGridLine) -> List[GridPosition]:
        """Given a line from pos1 to pos2, subdivide the area in
        this GridRect repeatedly, until we have the minimal list of
        grid squares that include some part of the line."""

        rects = self.Subdivide(line)

        if (len(rects) == 1) and rects[0].IsMinimum():
            # No further subdivision is possible
            return [rects[0].Position()]

        else:
            # More subdivision is possible
            positions: List[GridPosition] = []
            for rect in rects:
                positions.extend(rect.RecursiveSubdivide(line))
            return positions

def Line_To_Grid_Positions(line: GridLine) -> List[GridPosition]:
    """Convert a line between two grid squares into a list of grid squares that
    contain some part of the line."""
    # line from pos1 to pos2
    (pos1, pos2) = line
    (x1, y1) = pos1
    (x2, y2) = pos2

    # make bounding box
    left = min(x1, x2)
    right = max(x1, x2) + 1
    top = min(y1, y2)
    bottom = max(y1, y2) + 1
    bbox = GridRect((left, top), (right, bottom))

    # Get minimal set of grid positions by repeated subdivision
    return bbox.RecursiveSubdivide(line)

def Intersects_Grid_Square(gpos: GridPosition, ab: GridLine) -> bool:
    """Return true if line ab intersects this grid square."""
    (x1, y1) = gpos
    return GridRect((x1, y1), (x1 + 1, y1 + 1)).Intersects(ab)

