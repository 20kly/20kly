#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# Mysterious alien attackers.
# Look away now, unless you want to understand how the aliens work.

import math , pygame


import extra , sound
from quiet_season import Quiet_Season
import game_random
from primitives import *
from game_types import *
import network, map_items
from grid import Grid_To_Scr

Target = Tuple[Tuple[float, FloatGridPosition], map_items.Item]

alien_firing_sound: Optional[sound.Persisting_Sound] = None

class Alien_Season(Quiet_Season):
    def __init__(self, net: network.Network, alien_tech_level: float) -> None:
        Quiet_Season.__init__(self, net)
        self.alien_tech_level = alien_tech_level
        self.__Compute_Targets(5)
        self.alien_list: List[Alien] = []
        self.name = "Alien"
        self.new_aliens = False
        self.t2_announced = False



    def __Compute_Targets(self,m: int) -> None:
        # Analyse your network to determine the strategy
        # that will be used by the aliens.
        # The aliens may choose to attack the pipe that is
        # carrying the most current (this is the most
        # likely strategy)

        most_current: List[Target] = [ ((abs(pipe.current_n1_to_n2), pipe.n1.pos), pipe)
                for pipe in self.net.pipe_list ]
        extra.Sort_By_Tuple_0(most_current)

        #print 'Highest current:'
        #for (score, pipe) in most_current[ -( m * 2 ): ]:
        #    print score,pipe.n1.pos,'to',pipe.n2.pos
        target = most_current[ -( m * 2 ): ]

        # Or they may choose to attack the node with the most
        # connections
        most_conns: List[Target] = [ ((len(node.pipes), node.pos), node)
                for node in self.net.node_list ]
        extra.Sort_By_Tuple_0(most_conns)

        #print 'Most conns:'
        #for (score, node) in most_conns[ -m: ]:
        #    print score,node.pos
        target += most_conns[ -m: ]

        # Or they might attack the busiest steam generator.
        busy_generator = [ ((sum([ abs(pipe.current_n1_to_n2)
                        for pipe in node.pipes]), node.pos), node)
                for node in self.net.node_list
                if isinstance(node, map_items.Well_Node) ]
        extra.Sort_By_Tuple_0(busy_generator)

        #print 'Busy generator:'
        #for (score, node) in busy_generator[ -m: ]:
        #    print score,node.pos
        target += busy_generator[ -m: ]

        # TODO. Other attack strategies?

        # Aliens never attack the city.
        self.target_list = [ item for (score, item) in target
                        if not isinstance(item, map_items.City_Node) ]

    def Per_Period(self) -> None:
        if ( self.alien_tech_level >= 1.7 ):
            # More sophisticated aliens.
            # They replan their strategy before each wave.
            # They also concentrate on a smaller number of good targets.
            self.__Compute_Targets(3)

            if ( not self.t2_announced ):
                sound.FX("alient2")
                self.t2_announced = True

        # Make a wave of bug-eyed monsters. Here's where they start:
        num_aliens = self.net.demo.randint(2,2 + int(self.alien_tech_level))
        alien_angle = self.net.demo.random() * TWO_PI
        (cx,cy) = GRID_CENTRE
        alien_radius = cx + cy

        # Here's where they end up
        x = cx + ( alien_radius * math.cos(alien_angle + math.pi) )
        y = cy + ( alien_radius * math.sin(alien_angle + math.pi) )
        dest = map_items.Item("alien destination")
        dest.pos = (x,y)

        # Get target list for aliens
        num_targets = self.net.demo.randint(1,1 + int(self.alien_tech_level))
        self.net.demo.shuffle(self.target_list)
        alien_targets = self.target_list[ 0:num_targets ]
        alien_targets.append(dest)

        if ( len(alien_targets) == 1 ):
            # No targets! Therefore, no aliens.
            return

        for i in range(num_aliens):
            x = cx + ( alien_radius * math.cos(alien_angle) )
            y = cy + ( alien_radius * math.sin(alien_angle) )
            a = Alien(self.net)
            a.pos = (x,y)
            a.targets = [ item for item in alien_targets ]
            a.net = self.net
            a.alien_tech_level = self.alien_tech_level
            a.colour1 = (128, 0, 0)
            a.colour2 = (255, 100, 0)
            if ( self.t2_announced ):
                # Yellow aliens! Be scared!
                a.colour1 = (128, 128, 0)
                a.colour2 = (255, 200, 0)

            alien_angle += 0.15
            self.alien_list.append(a)

            self.new_aliens = True


        # We might be able to remove some aliens
        while (( len(self.alien_list) != 0 )
        and ( self.alien_list[ 0 ].done )):
            self.alien_list.pop(0)

    def Get_Period(self) -> int:
        return 16

    def Per_Frame(self, frame_time: float) -> None:
        for alien in self.alien_list:
            alien.Per_Frame(frame_time)

        if ( self.new_aliens ):
            sound.FX("ring")
            self.new_aliens = False

    def Draw(self, output: SurfaceType, update_area: UpdateAreaMethod) -> None:
        for alien in self.alien_list:
            alien.Draw(output, update_area)


    def Get_Extra_Info(self) -> List[StatTuple]:
        count = len([ x for x in self.alien_list if x.rookie ])
        if ( count != 0 ):
            return [ ((255,0,0), 16, "Aliens approaching!" )]
        else:
            return []

class Alien:
    def __init__(self, net: network.Network) -> None:
        self.pos: Optional[FloatSurfacePosition] = None  # set externally
        self.targets: List[map_items.Item] = []     # ditto
        self.net: Optional[network.Network] = None  # ditto
        self.alien_tech_level = 1.0                 # ditto
        self.colour1: Colour = (0, 0, 0)
        self.colour2: Colour = (0, 0, 0)
        self.net = net

        self.done = False
        self.rookie = True
        self.laser: Optional[Tuple[SurfacePosition, SurfacePosition]] = None
        self.current_target: Optional[map_items.Item] = None
        self.speed = 0.0
        self.attack_angle = 0.0
        self.points = [ (-1,-1) for i in range(3) ]
        self.countdown = 0.0
        self.rotation = 0.05 + ( self.net.demo.random() * 0.05 )
        self.bbox: Optional[RectType] = None


    ATTACK_DIST = 2.5
    MAX_DISTANCE_PER_SECOND = 14.0  # grid squares/second
    ACC_PER_SECOND_PER_SECOND = 0.4 # grid squares/second^2
    MAX_TIME_PER_TARGET = 1.2
    SIZE = 1

    def Per_Frame(self, frame_time: float) -> None:
        assert self.net is not None
        assert self.pos is not None
        self.laser = None
        if ( self.current_target is None ):
            # Retarget.
            if ( len(self.targets) == 0 ):
                self.done = True
                return
            self.current_target = self.targets.pop(0)
            self.countdown = self.MAX_TIME_PER_TARGET

            # Compute initial attack angle
            (x, y) = self.pos
            (tx, ty) = self.current_target.pos
            self.attack_angle = math.atan2( y - ty , x - tx )
            # Face target
            self.heading = self.attack_angle + math.pi

            self.in_zone = False
        else:
            fire = False
            (x, y) = self.pos
            (tx, ty) = self.current_target.pos
            aa = self.attack_angle
            tx += math.cos(aa) * self.ATTACK_DIST
            ty += math.sin(aa) * self.ATTACK_DIST
            ha = self.heading

            if ( self.in_zone ):
                # We're at the target zone.
                (x,y) = self.pos = (tx,ty)

                self.rookie = False
                self.attack_angle += self.rotation
                self.heading += self.rotation
                self.countdown -= frame_time
                if ( self.countdown < 0 ):
                    # time to move on to next target
                    self.current_target = None
                elif ( self.current_target.Take_Damage(self.alien_tech_level) ):
                    # Destroyed it!
                    self.net.Destroy(self.current_target, "aliens")
                    self.current_target = None
                else:
                    if isinstance(self.current_target, map_items.Building):
                        self.net.Popup(self.current_target)
                    fire = True
            else:
                dist = self.net.demo.hypot(tx - x, ty - y)
                if ( dist > 0.1 ):
                    # Still en-route to target zone
                    self.speed += self.ACC_PER_SECOND_PER_SECOND
                    if ( self.speed > self.MAX_DISTANCE_PER_SECOND ):
                        self.speed = self.MAX_DISTANCE_PER_SECOND
                    s = float(self.speed) * float(frame_time)

                    if ( s > dist ):
                        s = dist

                    x += math.cos(ha) * s
                    y += math.sin(ha) * s
                    self.pos = (x,y)
                else:
                    self.in_zone = True

            self.bbox = pygame.Rect(x,y,1,1)
            for (i,a) in enumerate([ 0, TWO_THIRDS_PI, - TWO_THIRDS_PI ]):
                px = int(x + ( math.cos(a + ha) * self.SIZE ))
                py = int(y + ( math.sin(a + ha) * self.SIZE ))
                (px,py) = Grid_To_Scr((px,py))
                self.points[ i ] = (int(px), int(py))
                self.bbox.union_ip(pygame.Rect(self.points[ i ], (1,1)))

            if ( fire ):
                assert self.current_target is not None
                px = int(self.current_target.pos[0])
                py = int(self.current_target.pos[1])
                tgt = Grid_To_Scr((px, py))
                self.laser = (self.points[ 0 ], tgt)
                self.bbox.union_ip(pygame.Rect(tgt, (1,1)))

            if ( fire and ( len(self.targets) != 0 )):
                global alien_firing_sound
                if alien_firing_sound is not None:
                    alien_firing_sound.Set(1.0)

    def Draw(self, output: SurfaceType, update_area: UpdateAreaMethod) -> None:
        pygame.draw.polygon(output, self.colour1, self.points)
        pygame.draw.polygon(output, self.colour2, self.points, 1)
        if ( self.laser is not None ):
            (a,b) = self.laser
            pygame.draw.line(output, (255, 255, 255), a, b)
        if ( self.bbox is not None ):
            update_area(self.bbox)


def Init_Aliens() -> None:
    global alien_firing_sound
    alien_firing_sound = sound.Persisting_Sound("clicker")

