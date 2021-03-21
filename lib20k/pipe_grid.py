#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

from . import map_items, intersect, bresenham
from .primitives import *
from .game_types import *


class Pipe_Grid:
    def __init__(self) -> None:
        self.pipe_grid: Dict[GridPosition, List[map_items.Pipe]] = dict()

    def Get_Pipes(self, gpos: GridPosition) -> "List[map_items.Pipe]":
        # Returns all pipes including ones already destroyed
        return self.pipe_grid.get(gpos, [])

    def Get_Pipe_Rotate(self, gpos: GridPosition) -> "Optional[map_items.Pipe]":
        # Returns one pipe (not destroyed) and rotates the list so that
        # other pipes can be selected.
        if not (gpos in self.pipe_grid):
            return None

        l = self.pipe_grid[gpos]

        while True:
            if len(l) == 0:
                return None

            out = l.pop(0)
            if not out.Is_Destroyed():
                l.append(out)
                return out

    def Get_Path(self, n1: "map_items.Node",
                n2: "map_items.Node") -> List[GridPosition]:

        # The original algorithm for determining the grid squares intersected by a pipe
        # was not completely accurate and made some glitches possible. This one is better.
        # There may be some (invalid) pipe and node placements that are no longer allowed.
        return intersect.Line_To_Grid_Positions((n1.pos, n2.pos))

    def Add_Pipe(self, pipe: "map_items.Pipe") -> None:
        # Add new pipe and garbage collect destroyed pipes
        for gpos in self.Get_Path(pipe.n1, pipe.n2):
            l = self.pipe_grid.get(gpos, [])
            l = [ p for p in l if not p.Is_Destroyed() ]
            l.append(pipe)
            self.pipe_grid[gpos] = l

class Storm_Pipe_Grid(Pipe_Grid):
    def Get_Path(self, n1: "map_items.Node",
                n2: "map_items.Node") -> List[GridPosition]:
        # Storms do AOE damage and behave differently if they use the new algorithm for
        # determining the grid squares intersected by a pipe. This causes regression tests
        # to fail - the game is subtly different. Therefore we still use the old algorithm
        # just for storm damage.

        (x1,y1) = n1.pos
        (x2,y2) = n2.pos
        def A(i):
            return ( 2 * i ) + 1

        return [ (x // 2, y // 2) for (x,y) in
                bresenham.Line((A(x1), A(y1)), (A(x2), A(y2))) ]

