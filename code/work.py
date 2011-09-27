# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Work units

import pygame
from pygame.locals import *

import steam_model, map_items
from primitives import *
from colours import *

# In population/frames. 
# i.e. 1 = work done by one person in one frame
WORK_UNIT_SIZE = 200 * steam_model.FRAME_RATE

# Amount of population/frames needed to build a node
BASE_NODE_WORK = WORK_UNIT_SIZE * 5

# Amount of population/frames needed to build a pipe of length 1 grid unit
BASE_PIPE_WORK = WORK_UNIT_SIZE / 4

# Velocity per frame
WORK_VELOCITY = FPX * 5 / steam_model.FRAME_RATE


MAX_WORK_UNITS_AT_NODE = 8



class Work_Unit:
    def __init__(self, start_node):
        self.selection = start_node
        self.pipe_toward_n2 = True
        self.pipe_dist_travelled = 0.0
        self.draw_pos = None
        self.selection.work_units += 1

    def Compute(self):
        self.draw_pos = None

        if self.selection == None:
            # Destroyed already
            return False

        elif self.selection.Needs_Work():
            # This looks like a job for a work unit!
            if isinstance(self.selection, map_items.Node):
                self.selection.work_units -= 1

            recalc = self.selection.Do_Work()
            self.selection = None
            return recalc

        elif isinstance(self.selection, map_items.Pipe):
            # On a Pipe. Follow specified direction.
            if self.pipe_dist_travelled >= self.selection.length_fp:
                # Reached the end, which is a node
                if self.pipe_towards_n2:
                    self.selection = self.selection.n2
                else:
                    self.selection = self.selection.n1

                assert isinstance(self.selection, map_items.Node)
                self.selection.work_units += 1
            else:
                # Still travelling - compute location
                self.pipe_dist_travelled += WORK_VELOCITY

                (x1, y1) = Grid_To_Scr(self.selection.n1.pos)
                (x2, y2) = Grid_To_Scr(self.selection.n2.pos)

                if not self.pipe_towards_n2:
                    (x1, x2) = (x2, x1)
                    (y1, y2) = (y2, y1)

                x = int(((x2 - x1) * self.pipe_dist_travelled) / 
                            self.selection.length_fp) + x1
                y = int(((y2 - y1) * self.pipe_dist_travelled) / 
                            self.selection.length_fp) + y1
                self.draw_pos = (x, y)

        else:
            # At Node. Decide outgoing direction
            assert isinstance(self.selection, map_items.Node)

            min_gradient = -1
            direction = None
            for pipe in self.selection.pipes:
                if pipe.work_gradient < min_gradient:
                    min_gradient = pipe.work_gradient
                    direction = pipe

            if ((direction == None)
            or (direction.work_gradient >= self.selection.work_gradient)):
                pass

            elif direction.n1 == self.selection:
                self.selection.work_units -= 1
                self.pipe_towards_n2 = True
                self.selection = direction
                self.pipe_dist_travelled = 0.0
                return self.Compute()
            
            elif direction.n2 == self.selection:
                self.selection.work_units -= 1
                self.pipe_towards_n2 = False
                self.selection = direction
                self.pipe_dist_travelled = 0.0
                return self.Compute()

            # If no direction has been determined, stay in place.
            # Await orders 

            if self.selection.work_units > MAX_WORK_UNITS_AT_NODE:
                # Self-destruct - too many work units waiting here
                self.selection.work_units -= 1
                self.selection = None

        return False

    def Draw(self, output):
        if ((self.draw_pos != None)
        and (self.selection != None)):
            pygame.draw.circle(output, WHITE, self.draw_pos, 4)

    def Is_Destroyed(self):
        return (self.selection == None)

