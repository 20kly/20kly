# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 

import math , pygame
from pygame.locals import *

import extra , particle , sound
from quiet_season import Quiet_Season
from primitives import *
from map_items import *
from game_random import game_random


storm_sound = storm_graphics = None

def Init_Storms():
    # This is rather slow.
    global storm_graphics
    storm_graphics = particle.Make_Particle_Effect(particle.Storm_Particle)

    global storm_sound
    storm_sound = sound.Persisting_Sound("stormdmg", "stormbeeps")

class Storm_Season(Quiet_Season):
    def __init__(self, net, storm_difficulty):
        Quiet_Season.__init__(self, net)
        self.name = "Storm"
        self.storms = []
        self.storm_difficulty = storm_difficulty

        global storm_graphics
        assert ( storm_graphics != None )

    def Get_Period(self):
        return 20

    def Per_Period(self):
        self.storms.append(Storm(self.net, self.storm_difficulty))
        removal = []
        for (i, s) in enumerate(self.storms):
            if ( s.Is_Offscreen() ):
                removal.insert(0, i)
        for i in removal:
            self.storms.pop(i)

    def Draw(self, output, update_area):
        for s in self.storms:
            s.Draw(output, update_area)
            
    def Get_Extra_Info(self):
        return [] #[ ((255,0,0), 16, "Storms are coming!" )]

    def Per_Frame(self, frame_time):
        for s in self.storms:
            s.Think(frame_time)


class Storm:
    def __init__(self, net, difficulty):
        self.net = net
        self.difficulty = difficulty
        self.storm_frame = 0

        [a, b] = extra.Make_Quake_SF_Points(5)
        if ( game_random.randint(0,1) == 0 ):
            (a, b) = (b, a) # flip - ensures start point is not always on top or left

        (self.pos, dest) = (a, b)

        (sx,sy) = self.pos
        (tx,ty) = dest
        dx = tx - sx
        dy = ty - sy
       
        speed = (( game_random.random() * 1.5 ) + 0.6 ) * self.difficulty

        # Convert the overall displacement vector (dx,dy) into a velocity.
        distance = game_random.hypot(dx,dy)
        self.velocity = extra.Partial_Vector((0, 0), (dx, dy), (speed, distance))

        # How long does this storm live?
        self.countdown = distance / speed


    def Draw(self, output, update_area):
        global storm_graphics
        sfx = storm_graphics[ self.storm_frame ]

        r = sfx.get_rect()
        r.center = Grid_To_Scr(self.pos)
        (x, y) = r.topleft
        x = int(x)
        y = int(y)
        r.topleft = (x,y)
        #pygame.draw.rect(output, (255,255,255), r, 1)
        output.blit(sfx, r.topleft)
        update_area(r)

    def Think(self, frame_time):
        # Do damage to things within the storm
        (cx,cy) = self.pos
        cx = int(cx)
        cy = int(cy)

        dmg = STORM_DAMAGE * self.difficulty

        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                key = (x,y)

                global storm_sound

                if ( self.net.pipe_grid.get(key, None) ):
                    for pipe in self.net.pipe_grid[ key ]:
                        if (( not pipe.Is_Destroyed() )
                        and ( pipe.Take_Damage(dmg) )):
                            self.net.Destroy(pipe, "storms")
                            storm_sound.Set(1.0)

                if ( self.net.ground_grid.get(key, None) ):
                    node = self.net.ground_grid[ key ]

                    if (( not node.Is_Destroyed() )
                    and ( node.Take_Damage(dmg) )):
                        self.net.Destroy(node, "storms")
                        storm_sound.Set(1.0)

        # Move
        (x,y) = self.pos
        (dx,dy) = self.velocity
        dx *= frame_time
        dy *= frame_time
        #print (x,y),(dx,dy)
        self.pos = (x + dx, y + dy)

        global storm_graphics
        self.storm_frame = ( self.storm_frame + 1 ) % len(storm_graphics)

        self.countdown -= frame_time

    def Is_Offscreen(self):
        return ( self.countdown < 0 )


