# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 

# Sorry, this isn't anything to do with IP: the Network is 
# the steam transport network.

import math , random , time , sound

import extra
from map_items import *
from primitives import *
from mail import New_Mail


class Network:
    def __init__(self, teaching):
        self.ground_grid = dict()
        self.pipe_grid = dict()
        self.well_list = []
        self.node_list = []
        self.pipe_list = []

        # UI updates required?
        self.dirty = False
    
        # Popup health meters may appear
        self.popups = set([])

        # Wells are created. All wells must be at least a certain
        # distance from the city.
        for i in xrange(10):
            self.Make_Well(teaching)

        # Get centre: 
        (x,y) = GRID_CENTRE

        # An additional bootstrap well, plus node, is created close to the city.
        wgpos = (x + 5,y + random.randint(-3,3))
        w = Well(wgpos)
        self.Add_Grid_Item(w)
        wn = Well_Node(wgpos)
        self.Add_Finished_Node(wn)
        wn.tutor_special = True

        # City is created.
        cn = City_Node((x,y))
        self.Add_Finished_Node(cn)

        # Pipe links the two
        self.Add_Pipe(cn,wn)
        pipe = cn.pipes[ 0 ]
        pipe.health = pipe.max_health
        pipe.Do_Work()

        # Final setup
        self.hub = cn # hub := city node

        self.connection_value = 1
        self.Work_Pulse(0) # used to make connection map


    def Add_Finished_Node(self, node):
        node.health = node.max_health
        node.Do_Work()
        node.complete = True
        self.Add_Grid_Item(node)

    def Add_Grid_Item(self, item, inhibit_effects=False):
        gpos = item.pos
        if ( item.Is_Destroyed() ):
            if ( not inhibit_effects ):
                New_Mail("Item is destroyed.")
            return False

        if ( self.pipe_grid.has_key(gpos) ):
            # There might be a pipe in the way. Then again,
            # it may have been destroyed already.
            for pipe in self.pipe_grid[ gpos ]:
                if ( pipe.Is_Destroyed() ):
                    continue

                if ( extra.Intersect_Grid_Square(gpos, 
                            (pipe.n1.pos, pipe.n2.pos)) ):
                    if ( not inhibit_effects ):
                        New_Mail("Can't build there - pipe in the way!")
                        sound.FX("error")
                    return False

        if (( self.ground_grid.has_key(gpos) )
        and ( isinstance(self.ground_grid[ gpos ], Building) )):
            if ( not inhibit_effects ):
                New_Mail("Can't build there - building in the way!")
                sound.FX("error")
            return False

        if ( isinstance(item, Node) ):
            self.node_list.append(item)
            if ( self.ground_grid.has_key( gpos )):
                item.Save(self.ground_grid[ gpos ])
            self.ground_grid[ gpos ] = item
        elif ( isinstance(item, Well) ):
            self.well_list.append(item)
            self.ground_grid[ gpos ] = item
        else:
            assert False # unknown type!

        return True

    def Is_Connected(self, node):
        assert isinstance(node, Building)
        return ( node.connection_value == self.connection_value )

    def Work_Pulse(self, work_points):
        # Connection map is built up. Process is
        # recursive: a wavefront spreads out across the net.
        #
        # At the same time, find the first node that needs work doing,
        # and do work at it.
        used = 0
        now = set([ self.hub ])
        self.connection_value += 1
        cv = self.connection_value
        while ( len(now) != 0 ):
            next = set([])
            for node in now:
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

    def Popup(self, node):
        if ( node != None ):
            self.popups |= set([node])
            node.popup_disappears_at = time.time() + 4.0

    def Expire_Popups(self):
        t = time.time()
        remove = set([])
        for node in self.popups:
            if ( node.popup_disappears_at <= t ):
                remove |= set([node])
        self.popups -= remove

    def Steam_Think(self):
        for n in self.node_list:
            n.Steam_Think()


    def Add_Pipe(self, n1, n2):

        if ( n1.Is_Destroyed() or n2.Is_Destroyed() ):
            sound.FX("error")
            New_Mail("Nodes are destroyed.")
            return False

        # What's in the pipe's path? 
        path = extra.More_Accurate_Line(n1.pos, n2.pos)
       
        other_pipes = set([])
        other_items = set([])
        for gpos in path:
            if ( self.pipe_grid.has_key(gpos) ):
                other_pipes |= set(self.pipe_grid[ gpos ])
            elif ( self.ground_grid.has_key(gpos) ):
                other_items |= set([self.ground_grid[ gpos ]])
        other_items -= set([n1,n2])
        if ( len(other_items) != 0 ):
            sound.FX("error")
            New_Mail("Pipe collides with other items.")
            print repr(other_items)
            return False

        for p in other_pipes:
            if ( not p.Is_Destroyed () ):
                if ((( p.n1 == n1 ) and ( p.n2 == n2 ))
                or (( p.n1 == n2 ) and ( p.n2 == n1 ))):
                    sound.FX("error")
                    New_Mail("There is already a pipe there.")
                    return False
                if ( intersect.Intersect((p.n1.pos,p.n2.pos),
                            (n1.pos,n2.pos)) != None ):
                    sound.FX("error")
                    New_Mail("That crosses an existing pipe.")
                    return False

        sound.FX("bamboo1")
        pipe = Pipe(n1, n2)
        self.pipe_list.append(pipe)

        for gpos in path:
            if ( not self.pipe_grid.has_key(gpos) ):
                self.pipe_grid[ gpos ] = [pipe]
            else:
                self.pipe_grid[ gpos ].append(pipe)
        return True

    def Get_Pipe(self, gpos):
        if ( not self.pipe_grid.has_key(gpos) ):
            return None
        l = self.pipe_grid[ gpos ]

        # Remove destroyed pipes
        l2 = [ pipe for pipe in l if not pipe.Is_Destroyed() ]

        # Did it change? Save it again if it did,
        # to save future recomputation.
        if ( len(l2) != len(l) ):
            self.pipe_grid[ gpos ] = l = l2

        if ( len(l) == 0 ):
            return None
        elif ( len(l) == 1 ):
            return l[ 0 ]
        else:
            # Juggle list
            out = l.pop(0)
            l.append(out)
            return out

    def Pipe_Possible(self, (x1,y1), (x2,y2)):
        # no restrictions
        return True
       
    def Destroy(self, node, by=None):
        if ( isinstance(node, Pipe) ):
            self.__Destroy_Pipe(node)
            return

        if (( node == self.hub )
        or ( not isinstance(node, Building) )):
            return # indestructible

        sound.FX("destroy")

        if ( isinstance(node, Node) ):
            # work on a copy, as __Destroy_Pipe will change the list.
            pipe_list = [ pipe for pipe in node.pipes ]
            for pipe in pipe_list:
                self.__Destroy_Pipe(pipe)

        gpos = node.pos
        if ( not self.ground_grid.has_key( gpos ) ):
            return # not on map
        if ( self.ground_grid[ gpos ] != node ):
            return # not on map (something else is there)

        self.dirty = True

        if ( by != None ):
            New_Mail(node.name_type + " destroyed by " + by + ".")
        

        node.Prepare_To_Die()
        self.__List_Destroy(self.node_list, node)
        rnode = node.Restore()

        if ( rnode == None ):
            del self.ground_grid[ gpos ]
        else:
            self.ground_grid[ gpos ] = rnode
        
    def __Destroy_Pipe(self, pipe):
        self.dirty = True
        pipe.Prepare_To_Die()
        self.__List_Destroy(self.pipe_list, pipe)
        self.__List_Destroy(pipe.n1.pipes, pipe)
        self.__List_Destroy(pipe.n2.pipes, pipe)


        #path = bresenham.Line(pipe.n1.pos, pipe.n2.pos)
        #for gpos in path:
        #    if ( self.pipe_grid.has_key(gpos) ):
        #        l = self.pipe_grid[ gpos ]
        #        self.__List_Destroy(l, pipe)
        #        if ( len(l) == 0 ):
        #            del self.pipe_grid[ gpos ]

   
    def __List_Destroy(self, lst, itm):
        l = len(lst)
        for i in reversed(xrange(l)):
            if ( lst[ i ] == itm ):
                assert itm == lst.pop(i)

    def Make_Well(self, teaching=False, inhibit_effects=False):
        self.dirty = True
        (x, y) = (cx, cy) = GRID_CENTRE
        (mx, my) = GRID_SIZE

        while (( self.ground_grid.has_key( (x,y) ))
        or ( math.hypot( x - cx, y - cy ) < 10 )):
            x = random.randint(0, mx - 1)
            y = random.randint(0, my - 1)
            if ( teaching ):
                if ( x < cx ):
                    x += cx

        w = Well((x,y))
        self.Add_Grid_Item(w, inhibit_effects or teaching)


    def Make_Ready_For_Save(self):
        for p in self.pipe_list:
            p.Make_Ready_For_Save()
            
            
        

