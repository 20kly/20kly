# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Sorry, this isn't anything to do with TCP/IP: the Network is 
# the steam transport network.

import random, time, sound, collections

import extra, work, trig, steam_model, lp

from map_items import *
from primitives import *
from mail import New_Mail


class Network:
    def __init__(self, teaching, seed):
        self.ground_grid = dict()
        self.pipe_grid = dict()
        self.well_list = []
        self.node_list = []
        self.pipe_list = []
        self.work_queue = collections.deque()
        self.rng = random.Random(seed)

        # Popup health meters may appear
        self.popups = set([])

        # Wells are created. All wells must be at least a certain
        # distance from the city.
        for i in xrange(10):
            self.Make_Well(teaching)

        # Get centre: 
        (x,y) = GRID_CENTRE

        # An additional bootstrap well, plus node, is created close to the city.
        wgpos = (x + 5, y + self.random(7) - 3)
        w = Well(wgpos)
        self.Add_Grid_Item(w)
        wn = Well_Node(wgpos)
        self.__Add_Finished_Node(wn)
        wn.tutor_special = True

        # City is created.
        self.city1 = cn = City_Node((x,y))
        self.__Add_Finished_Node(cn)

        # Pipe links the two
        self.Add_Pipe(cn,wn)
        pipe = cn.pipes[ 0 ]
        pipe.health = pipe.max_health
        pipe.Do_Work()

        # Network initialisation
        self.work_dirty = True
        self.steam_dirty = True
        self.__Calc_Gradients()
        self.__Calc_Steam()

    # PUBLIC. 
    def random(self, limit):
        """Return pseudorandom number, generated from network's seed."""
        assert limit > 0
        return self.rng.randrange(0, limit)

    # PRIVATE. Steam model.
    def __Calc_Steam(self):

        if not self.steam_dirty:
            return

        self.steam_dirty = False
        model = lp.ILP_Solver()
        lookup = dict()
        minimise = ["0"]

        for n in self.node_list:
            n.transfer = 0

            if n.Needs_Work():
                continue
    
            surrounding = []
            for p in n.pipes:
                if not (p.Needs_Work()
                or p.n1.Needs_Work() or p.n2.Needs_Work()):
                    for sub_pipe in xrange(len(steam_model.SUB_PIPES)):
                        if n == p.n1:
                            # Pipe represents outgoing current
                            surrounding.append('+%s_A%d' % (p.uid, sub_pipe))
                            surrounding.append('-%s_B%d' % (p.uid, sub_pipe))
                        else:
                            # Pipe represents incoming current
                            surrounding.append('-%s_A%d' % (p.uid, sub_pipe))
                            surrounding.append('+%s_B%d' % (p.uid, sub_pipe))

            if len(surrounding) == 0:
                # No connection to anything
                continue

            if isinstance(n, Well_Node):
                well_current_limit = n.Get_Current_Limit()

                # Another pipe from the well, representing well current
                surrounding.append("-")
                surrounding.append(n.uid)
                model.Add_Var(n.uid, lp.VAR_POSITIVE)
                model.Add_Term(n.uid, "<=", "%u" % well_current_limit)
                lookup[ n.uid ] = n

                # What is the loss? This is whatever the well could have
                # produced, but did not
                luid = "loss_" + n.uid
                model.Add_Var(luid, lp.VAR_POSITIVE)
                model.Add_Term(luid, "=", "%u - %s" % (
                                well_current_limit, n.uid))
                model.Add_Term(luid, "<=", "%u" % well_current_limit)

                # The loss must be minimised
                minimise.append("+%u*%s" % (steam_model.SOURCE_LOSS, luid))

            if isinstance(n, City_Node):
                # Another pipe to the city, representing outgoing current
                # n.b. this is unbounded, and the only current flow
                # that does not incur any loss
                cuid = "city_" + n.uid
                surrounding.append("+")
                surrounding.append(cuid)
                model.Add_Var(cuid, lp.VAR_POSITIVE)
                lookup[ cuid ] = n

            # Kirchoff's current law
            model.Add_Term("0", "=", "".join(surrounding))

        for p in self.pipe_list:
            p.velocity = 0
            p.pipe_loss = 0
            p.max_pipe_loss = 0

            if p.Needs_Work():
                continue
            if p.n1.Needs_Work() or p.n2.Needs_Work():
                continue

            # Permitted directions of travel
            allow_n2_to_n1 = allow_n1_to_n2 = True

            if isinstance(p.n1, City_Node):
                allow_n1_to_n2 = False 
            if isinstance(p.n2, City_Node):
                allow_n2_to_n1 = False 

            # Pipe is decomposed into multiple subpipes each with
            # a different cost function, this means it may be more
            # economical to build additional pipes than try to push
            # everything through one (but with diminishing returns)
            sub_pipes = p.Get_Subpipes()
            for (i, (resistance, current_limit)) in enumerate(sub_pipes):

                p.max_pipe_loss += resistance * current_limit

                for (uid, toward_n2, not_zero) in [
                        ('%s_A%d' % (p.uid, i), True, allow_n1_to_n2),
                        ('%s_B%d' % (p.uid, i), False, allow_n2_to_n1) ]:

                    # Current through a subpipe:
                    model.Add_Var(uid, lp.VAR_POSITIVE)
                    
                    if not_zero:
                        model.Add_Term(uid, "<=", "%u" % current_limit)

                        # The loss must be minimised
                        minimise.append("+%u*%s" % (resistance, uid))

                        lookup[ uid ] = (p, toward_n2, resistance)


                    else:
                        model.Add_Term(uid, "=", "0")


        # Objective term
        model.Add_Problem(''.join(minimise))


        # Model is complete
        def Receive(uid, value):
            x = lookup.get(uid, None)
            if x == None:
                return

            if isinstance(x, Node):
                x.transfer = abs(value)
                return

            (p, toward_n2, resistance) = x
            assert isinstance(p, Pipe)

            if not toward_n2:
                value = -value

            if value != 0:
                p.velocity += value
                p.pipe_loss += resistance * abs(value)
                print 'pipe', uid, value, resistance, p.velocity

        model.Solve(Receive)
        print 'solved'

        for n in self.node_list:
            n.Compute()

    # PRIVATE. Work unit controller.
    def __Calc_Gradients(self):
        """The work_gradient field is filled out for every
        Node and Pipe to determine how work units should be routed."""

        if not self.work_dirty:
            return

        self.work_dirty = False

        # Initial state; items needing work have gradient 1
        todo = []
        for item_list in (self.node_list, self.pipe_list):
            for item in item_list:
                if item.Needs_Work():
                    item.work_gradient = -LARGE_NUMBER # Item priority
                    todo.append(item)

                else:
                    item.work_gradient = 0

        # Algorithm expands the low gradient wherever the
        # gradient of a neighbouring node or pipe can be reduced
        while len(todo) != 0:
            item = todo.pop()
            copy = item.work_gradient + 1

            if isinstance(item, Pipe):
                for node in [item.n1, item.n2]:
                    if node.work_gradient > copy:
                        node.work_gradient = copy
                        todo.append(node)

            else:
                for pipe in item.pipes:
                    if pipe.work_gradient > (copy + pipe.length_fp):
                        pipe.work_gradient = copy + pipe.length_fp
                        todo.append(pipe)

    # PUBLIC. Work commands from game loop.
    def Work_Generate(self, node):
        """This method causes the given City_Node to generate a work unit."""

        self.__Calc_Gradients()
        self.work_queue.append(work.Work_Unit(node))

    # PUBLIC. Methods to add things to the network.
    def Add_Grid_Item(self, item, inhibit_effects=False):
        """Add some item to the grid. Could be anything other
        than a pipe. inhibit_effects == True suppresses messages
        to the user."""

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
            self.__Add_Node(item)
        elif ( isinstance(item, Well) ):
            self.well_list.append(item)
            self.ground_grid[ gpos ] = item
        else:
            assert False # unknown type!

        return True

    def Add_Node_Pipe_Split(self, node):
        """Add some Node to the grid, splitting pipes encountered
        at that location. There must be at least one pipe!"""

        gpos = node.pos
        assert isinstance(node, Node)
        assert not node.Is_Destroyed()

        if not self.Is_Split_Possible(gpos):
            return False
    
        self.__Add_Node(node)

        # Split all pipes present
        orig_pipes = self.pipe_grid[ gpos ][:]
        for pipe0 in orig_pipes:
            if pipe0.Is_Destroyed():
                continue

            (pipe1, pipe2) = pipe0.Split(node)
            self.__Destroy_Pipe(pipe0)
            self.__Add_Pipe(pipe1)
            self.__Add_Pipe(pipe2)

        return True

    def Add_Pipe(self, n1, n2):
        """New pipe created and placed between nodes n1 and n2."""

        assert isinstance(n1, Node)
        assert isinstance(n2, Node)
        assert n1 != n2

        if ( n1.Is_Destroyed() or n2.Is_Destroyed() ):
            sound.FX("error")
            New_Mail("Nodes are destroyed.")
            return False

        if not self.Is_Pipe_Possible(n1.pos, n2.pos, [n1, n2], False):
            sound.FX("error")
            New_Mail("Pipe collides with other items.")
            return False

        sound.FX("bamboo1")
        pipe = Pipe(n1, n2)

        self.__Add_Pipe(pipe)
        return True

    # PUBLIC. Methods to interrogate the network.
    def Get_Pipe(self, gpos, commit):
        """Get a pipe at the stated grid position (if any).
        Deals with the possibility that there may be more than one
        if commit == True."""

        if ( not self.pipe_grid.has_key(gpos) ):
            return None

        l = self.pipe_grid[ gpos ]

        # Remove destroyed pipes
        l2 = [ pipe for pipe in l if not pipe.Is_Destroyed() ]

        # Did it change? Save it again if it did,
        # to save future recomputation.
        if len(l2) != len(l):
            self.pipe_grid[ gpos ] = l = l2

        if ( len(l) == 0 ):
            # No pipes remain
            del self.pipe_grid[ gpos ]
            return None

        elif ( len(l) == 1 ):
            return l[ 0 ]

        else:
            if commit:
                # More than one option, juggle list
                out = l.pop(0)
                l.append(out)
                return out
            else: 
                return l[ 0 ]

    def Is_Split_Possible(self, gpos):
        """Can the pipe(s) at gpos be split by the creation of a new
        node?"""

        # Do this first to clear out destroyed pipes
        if self.Get_Pipe(gpos, False) == None:
            return False # No, no pipes present

        if self.ground_grid.get(gpos, None) != None:
            return False # No, something else there

        return True

    def Is_Pipe_Possible(self, pos1, pos2, 
                    ignore_nodes, consider_pos2_intersect):
        """Decide if a pipe can be laid from grid position pos1
        to grid position pos2, optionally ignoring some obstacles."""
        (x1, y1) = pos1
        (x2, y2) = pos2
        distance = trig.Distance(x1 - x2, y1 - y2)
        if distance > MAX_PIPE_LENGTH:
            return False # Too long
        if pos1 == pos2:
            return False # Too short

        empty = []
        ends = (pos1, pos2)
        may_intersect = False
        checked = set()
        path = extra.More_Accurate_Line(pos1, pos2)

        if consider_pos2_intersect:
            # Check the ends of the new pipe to see if it will
            # need to intersect with an existing pipe
            if self.Get_Pipe(pos2, False) != None:
                may_intersect = self.Is_Split_Possible(pos2)
      
        # Look for other intersections
        for gpos in path:
            for p in self.pipe_grid.get(gpos, empty):
                if p in checked:
                    continue

                checked.add(p)
                if p.Is_Destroyed():
                    continue

                if may_intersect and (gpos == pos2):
                    continue # Ignore intersections here

                if intersect.Intersect((p.n1.pos, p.n2.pos), ends) != None:
                    return False # New pipe intersects existing pipe

                if ((p.n1.pos in ends) and (p.n2.pos in ends)):
                    return False # New pipe is on top of an old pipe

            if self.ground_grid.has_key(gpos):
                item = self.ground_grid[ gpos ]
                if not (item in ignore_nodes):
                    return False # Collides with node
    
        return True
      
    # PUBLIC. Methods to destroy objects on the network.
    def Destroy(self, node, by=None):
        if ( isinstance(node, Pipe) ):
            self.__Destroy_Pipe(node)
            return

        if (isinstance(node, City_Node)
        or not isinstance(node, Building)):
            return # indestructible

        sound.FX("destroy")

        if ( isinstance(node, Node) ):
            # work on a copy, as __Destroy_Pipe will change the list.
            pipe_list = node.pipes[:]
            for pipe in pipe_list:
                self.__Destroy_Pipe(pipe)

        gpos = node.pos
        if ( not self.ground_grid.has_key( gpos ) ):
            return # not on map
        if ( self.ground_grid[ gpos ] != node ):
            return # not on map (something else is there)


        if ( by != None ):
            New_Mail(node.name_type + " destroyed by " + by + ".")
        

        node.Prepare_To_Die()
        self.__List_Destroy(self.node_list, node)
        self.work_dirty = True
        self.steam_dirty = True
        rnode = node.Restore()

        if ( rnode == None ):
            del self.ground_grid[ gpos ]
        else:
            self.ground_grid[ gpos ] = rnode
    
    # PRIVATE. Low-level routines for manipulating the network
    def __Add_Node(self, node):
        """Low-level method to add a node to the network."""
        gpos = node.pos
        self.node_list.append(node)
        if ( self.ground_grid.has_key( gpos )):
            node.Save(self.ground_grid[ gpos ])
        self.ground_grid[ gpos ] = node
        self.work_dirty = True
        self.steam_dirty = True

    def __Add_Pipe(self, pipe):
        """Low-level method to add a pipe to the network."""
        self.pipe_list.append(pipe)
        path = extra.More_Accurate_Line(pipe.n1.pos, pipe.n2.pos)

        for gpos in path:
            if not self.pipe_grid.has_key(gpos):
                self.pipe_grid[ gpos ] = [ pipe ]
            else:
                self.pipe_grid[ gpos ].append(pipe)

        self.work_dirty = True
        self.steam_dirty = True

    def __Destroy_Pipe(self, pipe):
        pipe.Prepare_To_Die()
        self.__List_Destroy(self.pipe_list, pipe)
        self.__List_Destroy(pipe.n1.pipes, pipe)
        self.__List_Destroy(pipe.n2.pipes, pipe)
        self.work_dirty = True
        self.steam_dirty = True
   
    def __List_Destroy(self, lst, itm):
        l = len(lst)
        for i in reversed(xrange(l)):
            if ( lst[ i ] == itm ):
                assert itm == lst.pop(i)

    def __Add_Finished_Node(self, node):
        node.health = node.max_health
        node.Do_Work()
        node.complete = True
        self.Add_Grid_Item(node)

    # PUBLIC. Events that affect the network.
    def Make_Well(self, teaching=False, inhibit_effects=False):
        (x, y) = (cx, cy) = GRID_CENTRE
        (mx, my) = GRID_SIZE

        while (( self.ground_grid.has_key( (x,y) ))
        or ( trig.Distance(x - cx, y - cy) < 10 )):
            x = self.random(mx)
            y = self.random(my)
            if ( teaching ):
                if ( x < cx ):
                    x += cx

        w = Well((x,y))
        self.Add_Grid_Item(w, inhibit_effects or teaching)

    def Make_Ready_For_Save(self):
        for p in self.pipe_list:
            p.Make_Ready_For_Save()
            
    def Compute(self):
        """Called every frame. Network activity is advanced."""

        for n in self.node_list:
            if isinstance(n, City_Node):
                n.Compute_City(self)

        # Push work units around the map
        recalc = False
        self.__Calc_Gradients()
        for i in xrange(len(self.work_queue)):
            unit = self.work_queue.popleft()
            recalc = unit.Compute() or recalc
            if not unit.Is_Destroyed():
                self.work_queue.append(unit)

        if recalc:
            self.work_dirty = True
            self.steam_dirty = True

        self.__Calc_Steam()

        

