#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

import math , pygame


from . import extra, particle, sound
from .quiet_season import Quiet_Season
from .primitives import *
from .game_types import *
from . import network
from .grid import Float_Grid_To_Scr


storm_sound: Optional[sound.Persisting_Sound] = None
storm_graphics: Optional[List[SurfaceType]] = None

def Init_Storms() -> None:
    # This is rather slow.
    global storm_graphics
    storm_graphics = particle.Make_Particle_Effect(particle.Storm_Particle)

    global storm_sound
    storm_sound = sound.Persisting_Sound("stormdmg", "stormbeeps")

class Storm_Season(Quiet_Season):
    def __init__(self, net: network.Network,
                 storm_difficulty: float) -> None:
        Quiet_Season.__init__(self, net)
        self.name = "Storm"
        self.storms: List[Storm] = []
        self.storm_difficulty = storm_difficulty

        global storm_graphics
        assert ( storm_graphics is not None )

    def Get_Period(self) -> int:
        return 20

    def Per_Period(self) -> None:
        self.storms.append(Storm(self.net, self.storm_difficulty))
        removal: List[int] = []
        for (i, s) in enumerate(self.storms):
            if ( s.Is_Offscreen() ):
                removal.insert(0, i)
        for i in removal:
            self.storms.pop(i)

    def Draw(self, output: SurfaceType, update_area: UpdateAreaMethod) -> None:
        for s in self.storms:
            s.Draw(output, update_area)

    def Get_Extra_Info(self) -> List[StatTuple]:
        return [] #[ ((255,0,0), 16, "Storms are coming!" )]

    def Per_Frame(self, frame_time: float) -> None:
        for s in self.storms:
            s.Think(frame_time)


class Storm:
    def __init__(self, net: network.Network, difficulty: float) -> None:
        self.net = net
        self.difficulty = difficulty
        self.storm_frame = 0

        [a, b] = extra.Make_Quake_SF_Points(self.net.demo, 5)
        if ( self.net.demo.randint(0,1) == 0 ):
            (a, b) = (b, a) # flip - ensures start point is not always on top or left

        self.pos: FloatSurfacePosition
        (self.pos, dest) = (a, b)

        (sx,sy) = self.pos
        (tx,ty) = dest
        dx = tx - sx
        dy = ty - sy

        speed = (( self.net.demo.random() * 1.5 ) + 0.6 ) * self.difficulty

        # Convert the overall displacement vector (dx,dy) into a velocity.
        distance = self.net.demo.hypot(dx,dy)
        self.velocity = extra.Partial_Vector((0, 0), (dx, dy), (speed, distance))

        # How long does this storm live?
        self.countdown = distance / speed


    def Draw(self, output: SurfaceType, update_area: UpdateAreaMethod) -> None:
        global storm_graphics
        assert storm_graphics is not None
        sfx = storm_graphics[ self.storm_frame ]

        r = sfx.get_rect()
        (x, y) = Float_Grid_To_Scr(self.pos)
        r.centerx = int(x)
        r.centery = int(y)
        (x, y) = r.topleft
        x = int(x)
        y = int(y)
        r.topleft = (x,y)
        #pygame.draw.rect(output, (255,255,255), r, 1)
        output.blit(sfx, r.topleft)
        update_area(r)

    def Think(self, frame_time: float) -> None:
        # Do damage to things within the storm
        (cx,cy) = self.pos
        cx = int(cx)
        cy = int(cy)

        dmg = STORM_DAMAGE * self.difficulty

        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                key = (x,y)

                global storm_sound
                assert storm_sound is not None

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
        (px,py) = self.pos
        (dx,dy) = self.velocity
        dx *= frame_time
        dy *= frame_time
        self.pos = (px + dx, py + dy)

        global storm_graphics
        assert storm_graphics is not None
        self.storm_frame = ( self.storm_frame + 1 ) % len(storm_graphics)

        self.countdown -= frame_time

    def Is_Offscreen(self) -> bool:
        return ( self.countdown < 0 )


