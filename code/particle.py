#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#
#
# A generator for particle animations of various types (pick an appropriate
# factory class for your application)
# Particle animations are precomputed and put onto colour-keyed surfaces.
#

import pygame, math, random

from . import resource, draw_effects
from .primitives import *
from .game_types import *


MAX_STEAM_SIZE = 20
MAX_STORM_SIZE = 70


class Abstract_Particle:
    def Next(self) -> NextParticleType: # NO-COV
        return ((0, 0), (0, 0, 0, 0))

    def Max_Size(self) -> int:          # NO-COV
        return 0

    def Num_Particles(self) -> int:     # NO-COV
        return 0

    def Particle_Size(self) -> int:     # NO-COV
        return 0

# A puff of steam coming out of a vent or steam maker.
class Steam_Particle(Abstract_Particle):
    def __init__(self) -> None:
        m = self.Max_Size() // 2
        m1 = m - 1
        m2 = m + 1
        scale2 = draw_effects.Get_Scaled_Size(2)

        (self.x, self.y) = (float(random.randint(m1,m2)), float(self.Max_Size()))
        self.bright = float(random.randint(80,160))
        self.dx = ( random.random() * scale2 ) - 1.0
        self.dy = - (( random.random() * scale2 * 0.5 ) + 1.0 )
        self.ddx = 0.001 * scale2
        self.db = ( random.random() * 2.0 ) + 3.0

    def Next(self) -> NextParticleType:
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.95
        self.dy *= 0.95
        self.dx += self.ddx
        self.bright -= self.db
        if ( self.bright < 40 ):
            self.bright = 40
        b = int(self.bright)
        return ((self.x, self.y), (b, b, b, 255))

    def Max_Size(self) -> int:
        return draw_effects.Get_Scaled_Size(MAX_STEAM_SIZE)

    def Num_Particles(self) -> int:
        return 100

    def Particle_Size(self) -> int:
        return draw_effects.Get_Scaled_Size(2)

# Swirling particles in a scary sand storm!
class Storm_Particle(Abstract_Particle):
    def __init__(self) -> None:
        scale4 = draw_effects.Get_Scaled_Size(4) # eye of storm radius = 4.
        scale1 = scale4 * 0.25
        self.radius = scale4 + ( random.random() * scale1 * 1.8 )
        self.angle = random.random() * TWO_PI
        self.dr = (abs(random.normalvariate(0.0,0.15)) + 0.01) * scale1

        # Colour comes from an authentic set of alien storm colours.
        stormsample = resource.Load_Image(Images.stormsample)
        x = random.randint(0, stormsample.get_rect().width - 1)
        y = random.randint(0, stormsample.get_rect().height - 1)
        self.c = stormsample.get_at((x,y))

    def Next(self) -> NextParticleType:
        x = ( self.Max_Size() // 2 ) + ( self.radius * math.cos(self.angle) )
        y = ( self.Max_Size() // 2 ) + ( self.radius * math.sin(self.angle) )
        self.angle += 0.2 # angular velocity
        self.radius += self.dr
        return ((x,y), self.c)

    def Max_Size(self) -> int:
        return draw_effects.Get_Scaled_Size(MAX_STORM_SIZE)

    def Num_Particles(self) -> int:
        return 250

    def Particle_Size(self) -> int:
        return draw_effects.Get_Scaled_Size(3)



def Make_Particle_Effect(particle_class: typing.Callable[[],
                            Abstract_Particle]) -> List[SurfaceType]:
    # Generate base frames.
    NUM_FRAMES = 80

    p = particle_class()
    sz = p.Max_Size()
    particle_effect: List[SurfaceType] = [ pygame.Surface((sz, sz)) for i in range(NUM_FRAMES) ]

    for frame in particle_effect:
        frame.set_colorkey((0,0,0))

    sz = p.Particle_Size()

    for i in range(p.Num_Particles()):
        # note random starting point. Make transition from
        # frame NUM_FRAMES-1 to frame 0 as seamless as any
        # other frame transition.
        j = random.randint(0,len(particle_effect) - 1)

        particle = particle_class()

        for k in range(NUM_FRAMES):
            ((x,y),c) = particle.Next()
            r = pygame.Rect(0, 0, sz, sz)
            r.center = (int(x), int(y))
            pygame.draw.rect(particle_effect[ j ], c, r)

            if (( x < 0 ) or ( x >= p.Max_Size() )
            or ( y < 0 ) or ( y >= p.Max_Size() )):
                break
            j = ( j + 1 ) % NUM_FRAMES

    return particle_effect


