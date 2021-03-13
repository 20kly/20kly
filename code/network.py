#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

# Sorry, this isn't anything to do with IP: the Network is
# the steam transport network.

import math, time

from . import map_items, sound, game_random, intersect, pipe_grid
from .primitives import *
from .game_types import *
from .mail import New_Mail


class Network:
    def __init__(self, demo: "game_random.Game_Random",
                 teaching: bool) -> None:
        self.demo = demo
        self.ground_grid: Dict[GridPosition, map_items.Item] = dict()
        self.pipe_grid = pipe_grid.Pipe_Grid()
        self.storm_pipe_grid = pipe_grid.Storm_Pipe_Grid()
        self.well_list: List[map_items.Well] = []
        self.node_list: List[map_items.Node] = []
        self.pipe_list: List[map_items.Pipe] = []

        # UI updates required?
        self.dirty = False

        # Popup health meters may appear
        self.popups: typing.Set[map_items.Building] = set([])

        # Wells are created. All wells must be at least a certain
        # distance from the city.
        for i in range(10):
            self.Make_Well(teaching)

        # Get centre:
        (x,y) = GRID_CENTRE

        # An additional bootstrap well, plus node, is created close to the city.
        wgpos = (x + 5,y + self.demo.randint(-3,3))
        w = map_items.Well(wgpos)
        self.Add_Grid_Item(w)
        wn = map_items.Well_Node(wgpos)
        self.Add_Finished_Node(wn)
        wn.tutor_special = True

        # City is created.
        cn = map_items.City_Node((x,y))
        self.Add_Finished_Node(cn)

        # Pipe links the two
        pipe = self.Add_Pipe(cn,wn)
        assert pipe is not None
        pipe.health = pipe.max_health
        pipe.Do_Work()

        # Final setup
        self.hub: map_items.City_Node = cn # hub := city node

        self.connection_value = 1
        self.Work_Pulse(0) # used to make connection map


    def Add_Finished_Node(self, node: "map_items.Node") -> None:
        node.health = node.max_health
        node.Do_Work()
        node.complete = True
        self.Add_Grid_Item(node)

    def Add_Grid_Item(self, item: "map_items.Item",
                      inhibit_effects=False) -> bool:
        gpos = typing.cast(GridPosition, item.pos)
        if ( item.Is_Destroyed() ):
            if ( not inhibit_effects ):
                New_Mail("Item is destroyed.")
            return False

        # There might be a pipe in the way. Then again,
        # it may have been destroyed already.
        for pipe in self.pipe_grid.Get_Pipes(gpos):
            if ( pipe.Is_Destroyed() ):
                continue

            if intersect.Intersects_Node(gpos, (pipe.n1.pos, pipe.n2.pos)):
                if ( not inhibit_effects ):
                    New_Mail("Can't build there - pipe in the way!")
                    sound.FX("error")
                return False

        if ( isinstance(self.ground_grid.get(gpos, None), map_items.Building) ):
            if ( not inhibit_effects ):
                New_Mail("Can't build there - building in the way!")
                sound.FX("error")
            return False

        if ( isinstance(item, map_items.Node) ):
            self.node_list.append(item)
            self.ground_grid[gpos] = item

        elif ( isinstance(item, map_items.Well) ):
            self.well_list.append(item)
            self.ground_grid[gpos] = item
        else:
            return False # unknown type!

        return True

    def Is_Connected(self, node: "map_items.Building") -> bool:
        assert isinstance(node, map_items.Building)
        return ( node.connection_value == self.connection_value )

    def Work_Pulse(self, work_points: int) -> int:
        # Connection map is built up. Process is
        # recursive: a wavefront spreads out across the net.
        #
        # At the same time, find the first node that needs work doing,
        # and do work at it.
        used = 0
        now: typing.Set[map_items.Building] = set([ self.hub ])
        self.connection_value += 1
        cv = self.connection_value
        while ( len(now) != 0 ):
            next: typing.Set[map_items.Building] = set([])
            for node in sorted(now, key=lambda node:
                            (node.Manhattan_Distance_From(self.hub), node.pos)):
                if ( node.connection_value < cv ):
                    if (( work_points > 0 ) and node.Needs_Work() ):
                        node.Do_Work()
                        self.Popup(node)
                        work_points -= 1
                        used += 1
                    node.connection_value = cv
                    next |= set(node.Exits())
            now = next
        return used

    def Popup(self, node: "Optional[map_items.Building]") -> None:
        if ( node is not None ):
            self.popups |= set([node])
            node.popup_disappears_at = time.time() + 4.0

    def Expire_Popups(self) -> None:
        t = time.time()
        remove = set([])
        for node in self.popups:
            if ( node.popup_disappears_at <= t ):
                remove |= set([node])
        self.popups -= remove

    def Steam_Think(self) -> None:
        for n in self.node_list:
            n.Steam_Think(self)


    def Add_Pipe(self, n1: "map_items.Node", n2: "map_items.Node") -> "Optional[map_items.Pipe]":

        if ( n1.Is_Destroyed() or n2.Is_Destroyed() ):
            sound.FX("error")
            New_Mail("Nodes are destroyed.")
            return None

        # What's in the pipe's path?
        path = self.pipe_grid.Get_Path(n1, n2)
        other_pipes = set()
        other_items = set()
        for gpos in path:
            other_pipes |= set(self.pipe_grid.Get_Pipes(gpos))
            n = self.ground_grid.get(gpos, None)
            if n is not None:
                other_items.add(n)

        other_items.discard(n1)
        other_items.discard(n2)

        for n in other_items:
            if ((not n.Is_Destroyed())
            and (not isinstance(n, map_items.Well))
            and intersect.Intersects_Node(n.pos, (n1.pos, n2.pos))):
                sound.FX("error")
                New_Mail("Pipe collides with other items.")
                return None

        for p in other_pipes:
            if not p.Is_Destroyed ():
                if ((( p.n1 == n1 ) and ( p.n2 == n2 ))
                or (( p.n1 == n2 ) and ( p.n2 == n1 ))):
                    sound.FX("error")
                    New_Mail("There is already a pipe there.")
                    return None
                if intersect.Lines_Intersect((p.n1.pos, p.n2.pos), (n1.pos, n2.pos)):
                    sound.FX("error")
                    New_Mail("That crosses an existing pipe.")
                    return None

        sound.FX("bamboo1")
        pipe = map_items.Pipe(n1, n2, self)
        self.pipe_list.append(pipe)

        self.pipe_grid.Add_Pipe(pipe)
        self.storm_pipe_grid.Add_Pipe(pipe)

        return pipe

    def Get_Pipe(self, gpos: GridPosition) -> "Optional[map_items.Pipe]":
        return self.pipe_grid.Get_Pipe_Rotate(gpos)

    def Destroy(self, node: "map_items.Item", by="") -> None:
        if ( isinstance(node, map_items.Pipe) ):
            self.__Destroy_Pipe(node)
            return

        if (( node == self.hub )
        or ( not isinstance(node, map_items.Node) )):
            return # indestructible

        sound.FX("destroy")

        # work on a copy, as __Destroy_Pipe will change the list.
        pipe_list = [ pipe for pipe in node.pipes ]
        for pipe in pipe_list:
            self.__Destroy_Pipe(pipe)

        gpos = node.pos
        if self.ground_grid.get(gpos, None) != node:
            # Node is not on the map
            return

        # Find the well beneath a well node (if applicable)
        restore_node: Optional[map_items.Item] = None
        if isinstance(node, map_items.Well_Node):
            for n in self.well_list:
                if n.pos == gpos:
                    restore_node = n 

        self.dirty = True

        if ( by != "" ):
            New_Mail(node.name_type + " destroyed by " + by + ".")

        node.Prepare_To_Die()
        List_Destroy(self.node_list, node)

        # restore the well (if applicable)
        if restore_node is not None:
            self.ground_grid[gpos] = restore_node
        else:
            # space becomes blank
            del self.ground_grid[gpos]


    def __Destroy_Pipe(self, pipe: "map_items.Pipe") -> None:
        self.dirty = True
        pipe.Prepare_To_Die()
        List_Destroy(self.pipe_list, pipe)
        List_Destroy(pipe.n1.pipes, pipe)
        List_Destroy(pipe.n2.pipes, pipe)

    def Make_Well(self, teaching=False, inhibit_effects=False) -> None:
        self.dirty = True
        (x, y) = (cx, cy) = GRID_CENTRE
        (mx, my) = GRID_SIZE

        while (( (x, y) in self.ground_grid )
        or ( self.demo.hypot( x - cx, y - cy ) < 10 )):
            x = self.demo.randint(0, mx - 1)
            y = self.demo.randint(0, my - 1)
            if ( teaching ):
                if ( x < cx ):
                    x += cx

        w = map_items.Well((x,y))
        self.Add_Grid_Item(w, inhibit_effects or teaching)

    def Pre_Save(self) -> None:
        for p in self.pipe_list:
            p.Pre_Save()
        self.demo.Pre_Save()

    def Post_Load(self) -> None:
        self.demo.Post_Load()

    def Lose(self) -> None:
        for n in self.node_list:
            n.Lose()

def List_Destroy(lst: List[typing.Any], itm: typing.Any) -> None:
    if itm in lst:
        lst.remove(itm)

