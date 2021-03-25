#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import random, math

from lib20k.intersect import Lines_Intersect, Intersects_Grid_Square, Line_To_Grid_Positions
from lib20k.primitives import *
from lib20k.game_types import *
from lib20k import grid
from . import unit_test


def test_Intersect() -> None:

    r = random.Random(1)

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

        z = Lines_Intersect(((xa1,ya1),(xa2,ya2)),((xb1,yb1),(xb2,yb2)))
        assert z

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
        assert Intersects_Grid_Square((0, 0), (outside1, outside2)), (outside1, outside2)

    # Line through the square, not the middle - intersects
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 3) % 8]
        assert Intersects_Grid_Square((0, 0), (outside1, outside2))

    # Line touching the corners of the square - intersects
    for i in range(1, 8, 2):
        outside1 = surround[i]
        outside2 = surround[(i + 2) % 8]
        assert Intersects_Grid_Square((0, 0), (outside1, outside2))

    # Line past the square
    for i in range(0, 8, 2):
        outside1 = surround[i]
        outside2 = surround[(i + 2) % 8]
        assert not Intersects_Grid_Square((0, 0), (outside1, outside2))

    # Line past the square
    for i in range(8):
        outside1 = surround[i]
        outside2 = surround[(i + 1) % 8]
        assert not Intersects_Grid_Square((0, 0), (outside1, outside2))

    # Line to the middle of the square - intersects
    for i in range(8):
        outside = surround[i]
        assert Intersects_Grid_Square((0, 0), (outside, (0, 0)))
        assert Intersects_Grid_Square((0, 0), ((0, 0), outside))


def test_Pipe_Grid_Paths() -> None:
    test_surface = unit_test.Setup_For_Unit_Test()

    grid_size = min(GRID_SIZE)  # minimum grid size 50

    r = random.Random(1)
    for cycle in range(100):
        # pick two grid squares
        x1 = r.randrange(2, grid_size - 2)
        x2 = r.randrange(2, grid_size - 2)
        y1 = r.randrange(2, grid_size - 2)
        y2 = r.randrange(2, grid_size - 2)
        Line_Test((x1, y1), (x2, y2), test_surface)


def Line_Test(pos1: GridPosition, pos2: GridPosition, test_surface: SurfaceType) -> None:
    # get positions
    (x1, y1) = pos1
    (x2, y2) = pos2
    if pos1 == pos2:
        # not a valid test
        return

    print("testing", pos1, pos2)

    square_size = grid.Get_Grid_Size()
    l1 = grid.Grid_To_Scr(pos1)
    l2 = grid.Grid_To_Scr(pos2)

    # link them together
    test_surface.fill((0, 0, 0))
    pygame.draw.line(test_surface, (255, 255, 255), l1, l2, 1)

    # this path should cover the line completely
    orig_path: typing.Set[GridPosition] = set(Line_To_Grid_Positions((pos1, pos2)))

    # expand the path to include all neighbours
    expanded_path: typing.Set[GridPosition] = set()
    for gpos in orig_path:
        (x1, y1) = gpos
        for y2 in range(y1 - 1, y1 + 2):
            for x2 in range(x1 - 1, x1 + 2):
                expanded_path.add((x2, y2))

    # find the true path based on the line drawn by pygame
    true_path: typing.Set[GridPosition] = set()
    square = pygame.Rect(0, 0, square_size, square_size)
    for gpos in sorted(expanded_path):
        square.center = grid.Grid_To_Scr(gpos)
        trigger = False
        for y3 in range(square.top, square.bottom):
            for x3 in range(square.left, square.right):
                c = test_surface.get_at((x3, y3))
                if c[0] != 0:
                    trigger = True
                    break
            if trigger:
                break

        if trigger:
            true_path.add(gpos)

    # Check true_path against orig_path
    missing_a_square = too_many_squares = 0
    for gpos in sorted(expanded_path):
        square.center = grid.Grid_To_Scr(gpos)
        if gpos in true_path:
            if gpos in orig_path:
                # orig_path is correct
                pygame.draw.rect(test_surface, (0, 128, 0), square, 0)
            else:  # NO-COV
                # orig_path is missing this square
                pygame.draw.rect(test_surface, (255, 0, 0), square, 0)
                missing_a_square += 1
                print("red: missing a square at", gpos)
        else:
            if gpos in orig_path:
                # orig_path has this square and maybe doesn't need it
                pygame.draw.rect(test_surface, (255, 0, 255), square, 0)
                too_many_squares += 1

    # Redraw line
    pygame.draw.line(test_surface, (255, 255, 255), l1, l2, 1)
    pygame.display.flip()

    # Not allowed any missing squares
    assert missing_a_square == 0
    assert too_many_squares < min(GRID_SIZE) 



