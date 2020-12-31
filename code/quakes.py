# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 
# 
# Here you can find full version of Quake, rewritten in pure Python
# and powered almost entirely by steam. 
#
# Well, not quite...

import math , pygame , random
from pygame.locals import *

import extra , intersect , sound
from quiet_season import Quiet_Season
from primitives import *
from map_items import *


class Quake_Season(Quiet_Season):
    def __init__(self, net, quake_difficulty):
        Quiet_Season.__init__(self, net)
        self.name = "Quake"
        self.state = self.START
        self.fault_lines = []
        self.unfurling = 0
        self.damage = quake_difficulty

    # Phases:
    START = 0
    QUAKE_WARNING = 2
    QUAKE = 5
    QUAKE_DAMAGE = 6
    QUAKE_AFTERMATH = 7
    RESET = 15

    def Get_Period(self):
        return 2

    def Per_Period(self):
        self.state += 1
        if ( self.state >= self.RESET ):
            self.state = self.START
            self.fault_lines = []
            self.unfurling = 0

        if ( self.state == self.QUAKE_WARNING ):
            sound.FX("firealrm")
        elif ( self.state == self.QUAKE ):
            self.__Generate_Quake()
        elif ( self.state == self.QUAKE_DAMAGE ):
            self.__Apply_Damage()

        if ( ( self.QUAKE - 1 ) <= self.state < self.QUAKE_AFTERMATH ):
            global quake_sound
            quake_sound.Set(1.0)
        elif ( self.state == self.QUAKE_AFTERMATH ):
            quake_sound.Fade_Out()

    def __Generate_Quake(self):
        # Make start/finish points first.
        line = extra.Make_Quake_SF_Points(2)

        # Split line, repeatedly, at random locations.
        for i in range(6,1,-1):
            split = random.randint(0,len(line) - 2)
            (x3, y3) = extra.Partial_Vector(line[ split ], line[ split + 1 ], 
                    (random.random(), 1.0) )
            # New vertex gets moved about a bit.
            x3 += ( random.random() * 2.0 * i ) - float(i)
            y3 += ( random.random() * 2.0 * i ) - float(i)
            line.insert(split + 1, (x3, y3))

        # Long segments of the line are reduced into shorter segments.
        # This isn't random.
        i = 0
        while ( i <= ( len(line) - 2 )):
            (x1, y1) = line[ i ]
            (x2, y2) = line[ i + 1 ]
            sz = math.hypot( x1 - x2, y1 - y2 )
            if ( sz > 10.0 ):
                (x3, y3) = extra.Partial_Vector(
                        line[ i ], line[ i + 1 ], (0.5, 1.0))
                line.insert(i + 1, (x3, y3))
            else:
                i += 1

        # Line may be reversed.
        if ( random.randint(0,1) == 0 ):
            line.reverse()

        self.fault_lines = line


    def __Apply_Damage(self):
        # Apply damage as appropriate
        damage_nodes = set([])
        destroy_pipes = set([])

        for i in xrange(len(self.fault_lines) - 1):
            gpos1 = self.fault_lines[ i ]
            gpos2 = self.fault_lines[ i + 1 ]
            # Any pipes that intersect gpos1 and gpos2 are destroyed.
            for pipe in self.net.pipe_list:
                if ( intersect.Intersect((pipe.n1.pos,pipe.n2.pos),
                        (gpos1, gpos2)) != None ):
                    destroy_pipes |= set([ pipe ])

        for pipe in destroy_pipes:
            damage_nodes |= set([ pipe.n1, pipe.n2 ])

        for pipe in destroy_pipes:
            self.net.Destroy(pipe, "quakes")

        for node in damage_nodes:
            # Nodes take damage. Calculate how much...
            # What's the distance from the fault line?
            # Use Manhattan distance to save needless effort.
            distance = max_dist = 10
            (nx, ny) = node.pos
            for (fx, fy) in self.fault_lines:
                distance = min([abs(fx - nx), abs(fy - ny), distance])

            dmg = (( max_dist - distance ) * self.damage )
            if ( dmg > 0 ):
                if ( node.Take_Damage(dmg) ):
                    self.net.Destroy(node, "quakes")

        if ( self.damage < 2.0 ):
            # Some Wells are created.

            num_wells = random.randint(0, 3)
            if ( num_wells == 1 ):
                New_Mail("A new steam well has appeared!")
            elif ( num_wells > 1 ):
                New_Mail("Some new steam wells have appeared!")
            for i in xrange(num_wells):
                self.net.Make_Well(False, True)

    def Draw(self, output, update_area):
        if ( self.QUAKE <= self.state <= self.QUAKE_AFTERMATH ):
            # Draw fault line
            fl = [ Grid_To_Scr(x) for x in self.fault_lines[ 0: self.unfurling ] ]
            if ( len(fl) > 1 ):
                pygame.draw.lines(output, (200,200,200), False, fl, 4)
                pygame.draw.lines(output, (0,0,0), False, fl, 2)
            update_area(output.get_rect())

        
    def Get_Extra_Info(self):
        if ( self.QUAKE_WARNING <= self.state < self.QUAKE ):
            return [ ((255,0,0), 16, "Quake warning!" )]
        return []

    def Is_Shaking(self):
        return ( self.state in [ self.QUAKE, self.QUAKE_DAMAGE ] )

    def Per_Frame(self, frame_time):
        if ( self.QUAKE <= self.state < self.QUAKE_AFTERMATH ):
            self.unfurling += 1
        elif ( self.state == self.QUAKE_AFTERMATH ):
            if ( len(self.fault_lines) > 0 ):
                self.fault_lines.pop(0) # the reverse of unfurling!


def Init_Quakes():
    global quake_sound
    quake_sound = sound.Persisting_Sound("earthquake")


