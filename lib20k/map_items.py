#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# Items that you will find on the map.
# All inherit from the basic Item.

import pygame, math


from . import partial_vector, stats, resource, draw_obj, sound
from .primitives import *
from .game_types import *
from . import steam_model, draw_effects, network
from .mail import New_Mail
from .difficulty import DIFFICULTY
from .grid import Grid_To_Scr, Get_Grid_Size, Grid_To_Scr_Rect

class Item:
    def __init__(self, xy: GridPosition, name: str) -> None:
        self.pos = xy
        self.name_type = name
        self.emits_steam = False
        self.tutor_special = False

    def Draw(self, output: SurfaceType) -> None:
        return None

    def Draw_Selected(self, output: SurfaceType, highlight: Colour) -> Optional[RectType]: # NO-COV
        return None

    def Draw_Popup(self, output: SurfaceType) -> Optional[RectType]: # NO-COV
        return None

    def Get_Information(self) -> List[StatTuple]:
        return [ ((255,255,0), 20, self.name_type) ]

    def Prepare_To_Die(self) -> None: # NO-COV
        pass

    def Take_Damage(self, dmg_level=1) -> bool:
        # Basic items have no health and therefore can't be damaged
        return False

    def Is_Destroyed(self) -> bool:
        return False

    def Sound_Effect(self) -> None: # NO-COV
        pass

    def Manhattan_Distance_From(self, other: "Item") -> float:
        (x1, y1) = self.pos
        (x2, y2) = other.pos
        return abs(x1 - x2) + abs(y1 - y2)

class Well(Item):
    def __init__(self, xy: GridPosition, name="Well") -> None:
        Item.__init__(self, xy, name)
        self.draw_obj = draw_obj.Draw_Obj(Images.well, 1)
        self.emits_steam = True


class Building(Item):
    def __init__(self, xy: GridPosition, name: str) -> None:
        Item.__init__(self, xy, name)
        self.health = 0
        self.complete = False
        self.was_once_complete = False
        self.max_health = 5 * HEALTH_UNIT
        self.base_colour = (255,255,255)
        self.connection_value = 0
        self.popup_countdown = 0
        self.destroyed = False
        self.tech_level = 1


    def Prepare_To_Die(self) -> None:
        self.popup_disappears_at = 0.0
        self.health = 0
        self.destroyed = True

    def Take_Damage(self, dmg_level=1) -> bool:
        x = int(dmg_level * DIFFICULTY.DAMAGE_FACTOR)
        self.health -= x
        if ( self.health <= 0 ):
            self.Prepare_To_Die()
            return True
        return False

    def Begin_Upgrade(self) -> None:
        pass

    def Exits(self) -> "typing.Sequence[Building]":
        return []

    def Is_Destroyed(self) -> bool:
        return self.destroyed

    def Needs_Work(self) -> bool:
        return ( self.max_health != self.health )

    def Is_Broken(self) -> bool:
        return self.Needs_Work()

    def Do_Work(self) -> None:
        if ( not self.destroyed ):
            if ( self.health < self.max_health ):
                self.health += WORK_UNIT_SIZE
            if ( self.health >= self.max_health ):
                self.health = self.max_health
                if ( self.was_once_complete ):
                    # An upgrade or repair
                    sound.FX(Sounds.double)
                else:
                    # Construction complete!
                    sound.FX(Sounds.whoosh1)
                self.complete = True
                self.was_once_complete = True

    def Get_Popup_Items(self) -> List[BarMeterStatTuple]:
        return [ self.Get_Health_Meter() ]

    def Get_Health_Meter(self) -> BarMeterStatTuple:
        return (self.health, (0,255,0), self.max_health, (255,0,0))

    def Draw_Popup(self, output) -> Optional[RectType]:
        (x,y) = Grid_To_Scr(self.pos)
        x -= draw_effects.Get_Scaled_Size(16)
        y -= draw_effects.Get_Scaled_Size(12)
        return stats.Draw_Bar_Meter(output, self.Get_Popup_Items(), (x,y),
                                    draw_effects.Get_Scaled_Size(32),
                                    draw_effects.Get_Scaled_Size(5))

    def Get_Tech_Level(self) -> str:
        return ("Tech Level %d" % self.tech_level)

    def Get_Information(self) -> List[StatTuple]:
        l = Item.Get_Information(self)
        h = (( self.health * 100 ) // self.max_health)
        h2 = (self.max_health - self.health)
        units = ""
        if ( h2 > 0 ):
            units = str(h2) + " more unit"
            if ( h2 != 1 ):
                units += "s"
            units += " req'd "

        if ( self.complete ):
            if ( self.health == self.max_health ):
                l += [ (self.Get_Diagram_Colour(), 15, "Operational") ]
            else:
                l += [ (self.Get_Diagram_Colour(), 15, "Damaged, " + str(h) + "% health"),
                       (None, None, self.Get_Health_Meter()),
                       ((128,128,128), 10, units + "to complete repairs")]

            l += [ ((128,128,0), 15, self.Get_Tech_Level()) ]
        else:
            if ( self.health > 0 ):
                l += [ (self.Get_Diagram_Colour(), 15, "Building, " + str(h) + "% done"),
                       (None, None, self.Get_Health_Meter()),
                       ((128,128,128), 10, units + "to finish building")]
            else:
                l += [ (self.Get_Diagram_Colour(), 15, "Not Built") ]

        return l

    def Get_Diagram_Colour(self) -> Colour:
        (r,g,b) = self.base_colour
        if ( self.complete ):
            if ( self.health < self.max_health ):
                g = ( self.health * g ) // self.max_health
                b = ( self.health * b ) // self.max_health
                if ( r < 128 ): r = 128
        else:
            if ( self.health > 0 ):
                r = ( self.health * r ) // self.max_health
                b = ( self.health * b ) // self.max_health
                if ( r < 128 ): r = 128
            else:
                r = g = b = 128
        return (r,g,b)

class Node(Building):
    def __init__(self, xy: GridPosition, name="Node") -> None:
        Building.__init__(self, xy, name)
        self.pipes: List[Pipe] = []
        self.max_health = NODE_HEALTH_UNITS * HEALTH_UNIT
        self.base_colour = (255,192,0)
        self.steam = steam_model.Steam_Model()
        self.draw_obj_finished = draw_obj.Draw_Obj(Images.node, 1)
        self.draw_obj_incomplete = draw_obj.Draw_Obj(Images.node_u, 1)
        self.draw_obj = self.draw_obj_incomplete

    def Begin_Upgrade(self):
        if ( self.tech_level >= NODE_MAX_TECH_LEVEL ):
            New_Mail("Node cannot be upgraded further.")
            sound.FX(Sounds.error)
        elif ( self.Needs_Work() ):
            New_Mail("Node must be operational before an upgrade can begin.")
            sound.FX(Sounds.error)
        else:
            sound.FX(Sounds.crisp)

            # Upgrade a node to get a higher capacity and more health.
            # More health means harder to destroy.
            # More capacity means your network is more resilient.
            self.tech_level += 1
            self.max_health += NODE_UPGRADE_WORK * HEALTH_UNIT
            self.complete = False
            self.steam.Capacity_Upgrade()

    def Steam_Think(self, net: "network.Network") -> None:
        nl: List[Tuple[steam_model.Steam_Model, float]] = []
        for p in self.Exits():
            if ( not p.Is_Broken() ):
                if ( p.n1 == self ):
                    if ( not p.n2.Is_Broken() ):
                        nl.append((p.n2.steam, p.resistance))
                else:
                    if ( not p.n1.Is_Broken() ):
                        nl.append((p.n1.steam, p.resistance))

        nd = self.steam.Think(nl, net)
        for (p, current) in zip(self.Exits(), nd):
            # current > 0 means outgoing flow
            if ( current > 0.0 ):
                p.Flowing_From(self, current)

        if ( self.Is_Broken() ):
            self.draw_obj = self.draw_obj_incomplete
        else:
            self.draw_obj = self.draw_obj_finished


    def Exits(self) -> "typing.Sequence[Pipe]":
        return self.pipes

    def Get_Popup_Items(self) -> List[BarMeterStatTuple]:
        return Building.Get_Popup_Items(self) + [
                self.Get_Pressure_Meter() ]

    def Get_Pressure_Meter(self) -> BarMeterStatTuple:
        return (int(self.Get_Pressure()), (100, 100, 255),
                    int(self.steam.Get_Capacity()), (0, 0, 100))

    def Get_Information(self) -> List[StatTuple]:
        return Building.Get_Information(self) + [
            ((128,128,128), 15, "Steam pressure: %1.1f P" % self.steam.Get_Pressure()) ]

    def Get_Pressure(self) -> float:
        return self.steam.Get_Pressure()

    def Draw(self, output: SurfaceType) -> None:
        self.draw_obj.Draw(output, typing.cast(GridPosition, self.pos), (0,0))

    def Draw_Selected(self, output: SurfaceType, highlight: Colour) -> Optional[RectType]:
        size2 = draw_effects.Get_Scaled_Size(2)
        ra = ( Get_Grid_Size() // 2 ) + size2
        pygame.draw.circle(output, highlight, Grid_To_Scr(self.pos), ra, size2 )
        return Grid_To_Scr_Rect(self.pos).inflate(ra,ra)

    def Sound_Effect(self) -> None:
        sound.FX(Sounds.bamboo)

    def Lose(self) -> None:
        self.steam.Lose()

class City_Node(Node):
    def __init__(self, xy: GridPosition, name="City") -> None:
        Node.__init__(self,xy,name)
        self.base_colour = CITY_COLOUR
        self.avail_work_units = 1
        self.city_upgrade = 0
        self.city_upgrade_start = 1
        self.draw_obj = draw_obj.Draw_Obj(Images.city1, 3)
        self.draw_obj_finished = self.draw_obj_incomplete = self.draw_obj
        self.total_steam = 0.0

    def Begin_Upgrade(self) -> None:
        # Upgrade a city for higher capacity
        # and more work units. Warning: upgraded city
        # will require more steam!
        #
        # Most upgrades use the health system as this
        # puts the unit out of action during the upgrade.
        # This isn't suitable for cities: you lose if your
        # city is out of action. We use a special system.
        if ( self.city_upgrade == 0 ):
            sound.FX(Sounds.mechanical_1)

            self.city_upgrade = self.city_upgrade_start = (
                ( CITY_UPGRADE_WORK + ( self.tech_level *
                DIFFICULTY.CITY_UPGRADE_WORK_PER_LEVEL )) * HEALTH_UNIT )
            self.avail_work_units += 1 # Extra steam demand
        else:
            New_Mail("City is already being upgraded.")
            sound.FX(Sounds.error)

    def Needs_Work(self) -> bool:
        return ( self.city_upgrade != 0 )

    def Is_Broken(self) -> bool:
        return False

    def Do_Work(self) -> None:
        if ( self.city_upgrade > 0 ):
            self.city_upgrade -= 1
            if ( self.city_upgrade == 0 ):
                self.tech_level += 1
                self.steam.Capacity_Upgrade()

                sound.FX(Sounds.cityups)
                New_Mail("City upgraded to level %d of %d!" %
                    ( self.tech_level, DIFFICULTY.CITY_MAX_TECH_LEVEL ) )

    def Get_Avail_Work_Units(self) -> int:
        return self.avail_work_units

    def Get_Steam_Demand(self) -> float:
        return (( self.avail_work_units *
                WORK_STEAM_DEMAND ) + STATIC_STEAM_DEMAND )

    def Get_Steam_Supply(self) -> float:
        supply = 0.0
        for pipe in self.pipes:
            if ( self == pipe.n1 ):
                supply -= pipe.current_n1_to_n2
            else:
                supply += pipe.current_n1_to_n2

        return supply

    def Get_Information(self) -> List[StatTuple]:
        l = Node.Get_Information(self)
        if ( self.city_upgrade != 0 ):
            l.append( ((255,255,50), 12, "Upgrading...") )
            l.append( (None, None, self.Get_City_Upgrade_Meter()) )
        return l

    def Get_City_Upgrade_Meter(self) -> BarMeterStatTuple:
        if ( self.city_upgrade == 0 ):
            return (0, (0,0,0), 1, (64,64,64))
        else:
            return (self.city_upgrade_start - self.city_upgrade, (255,255,50),
                 self.city_upgrade_start, (64,64,64))

    def Steam_Think(self, net: "network.Network") -> None:
        x = self.Get_Steam_Demand()
        self.total_steam += x
        self.steam.Source(- x)
        Node.Steam_Think(self, net)

    def Draw(self, output: SurfaceType) -> None:
        Node.Draw(self, output)

    def Get_Popup_Items(self) -> List[BarMeterStatTuple]:
        return [ self.Get_City_Upgrade_Meter() ,
                self.Get_Pressure_Meter() ]

    def Take_Damage(self, dmg_level=1) -> bool:  # Can't destroy a city.
        return False

    def Draw_Selected(self, output: SurfaceType, highlight: Colour) -> Optional[RectType]:
        r = Grid_To_Scr_Rect(self.pos).inflate(CITY_BOX_SIZE,CITY_BOX_SIZE)
        size2 = draw_effects.Get_Scaled_Size(2)
        pygame.draw.rect(output, highlight,r,size2)
        return r.inflate(size2,size2)

    def Get_Tech_Level(self) -> str:
        return Building.Get_Tech_Level(self) + (" of %d" % DIFFICULTY.CITY_MAX_TECH_LEVEL )

    def Sound_Effect(self) -> None:
        sound.FX(Sounds.computer)


class Well_Node(Node):
    def __init__(self, xy: GridPosition, name="Steam Maker") -> None:
        Node.__init__(self,xy,name)
        self.base_colour = (255,0,192)
        self.draw_obj_finished = draw_obj.Draw_Obj(Images.maker, 1)
        self.draw_obj_incomplete = draw_obj.Draw_Obj(Images.maker_u, 1)
        self.draw_obj = self.draw_obj_incomplete
        self.emits_steam = True
        self.production = 0


    def Steam_Think(self, net: "network.Network") -> None:
        if ( not self.Needs_Work() ):
            self.production = (DIFFICULTY.BASIC_STEAM_PRODUCTION + (self.tech_level *
                    DIFFICULTY.STEAM_PRODUCTION_PER_LEVEL))
            self.steam.Source(self.production)
        else:
            self.production = 0
        Node.Steam_Think(self, net)

    def Get_Information(self) -> List[StatTuple]:
        return Node.Get_Information(self) + [
            (self.base_colour, 15,
                "Steam production: %1.1f U" % self.production) ]

    def Sound_Effect(self) -> None:
        sound.FX(Sounds.bamboo1)


class Pipe(Building):
    def __init__(self, n1: Node, n2: Node,
                 net: "network.Network", name="Pipe") -> None:
        Building.__init__(self, (0, 0), name)
        assert n1 != n2
        n1.pipes.append(self)
        n2.pipes.append(self)
        self.n1 = n1
        self.n2 = n2
        (x1,y1) = n1.pos
        (x2,y2) = n2.pos

        self.pos = ((x1 + x2) // 2, (y1 + y2) // 2)
        self.length = net.demo.hypot(x1 - x2, y1 - y2)
        self.max_health = int(self.length + 1) * HEALTH_UNIT
        self.base_colour = (0,255,0)
        self.resistance: float = ( self.length + 2.0 ) * RESISTANCE_FACTOR
        self.current_n1_to_n2: float = 0.0

        self.dot_drawing_offset = 0
        self.dot_positions: List[FloatSurfacePosition] = []

    def Begin_Upgrade(self) -> None:
        if ( self.tech_level >= PIPE_MAX_TECH_LEVEL ):
            New_Mail("Pipe cannot be upgraded further.")
            sound.FX(Sounds.error)
        elif ( self.Needs_Work() ):
            New_Mail("Pipe must be operational before an upgrade can begin.")
            sound.FX(Sounds.error)
        else:
            sound.FX(Sounds.crisp)
            # Upgrade a pipe for lower resistance and more health.
            self.tech_level += 1
            self.max_health += int( PIPE_UPGRADE_WORK_FACTOR *
                        self.length * HEALTH_UNIT )
            self.complete = False
            self.resistance *= PIPE_UPGRADE_RESISTANCE_FACTOR

    def Exits(self) -> typing.Sequence[Node]:
        return [self.n1, self.n2]

    def Flowing_From(self, node: Node, current: float) -> None:
        if ( node == self.n1 ):
            self.current_n1_to_n2 = current
        else:
            assert node == self.n2
            self.current_n1_to_n2 = - current

    def Take_Damage(self, dmg_level=1) -> bool:
        # Pipes have health proportional to their length.
        # To avoid a rules loophole, damage inflicted on
        # pipes is multiplied by their length. Pipes are
        # a very soft target.
        return Building.Take_Damage(self, dmg_level * (self.length + 1.0))

    def Draw(self, output: SurfaceType) -> None:
        (x1,y1) = Grid_To_Scr(self.n1.pos)
        (x2,y2) = Grid_To_Scr(self.n2.pos)
        size3 = draw_effects.Get_Scaled_Size(3)

        if ( self.Needs_Work() ):
            # Plain red line
            pygame.draw.line(output, (255,0,0), (x1,y1), (x2,y2), size3)
            self.dot_drawing_offset = 0
            return


        # Dark green backing line:
        colour = (32,128,20)
        pygame.draw.line(output, colour, (x1,y1), (x2,y2), size3)

        if ( self.current_n1_to_n2 == 0.0 ):
            return

        size1 = max(1, size3 // 3)
        r = pygame.Rect(0,0,size1,size1)
        for pos in self.dot_positions:
            r.center = (int(pos[0]), int(pos[1]))
            output.fill(colour, r)

        # Thanks to Acidd_UK for the following suggestion.
        dots = int(( self.length * 0.3 ) + 1.0)
        positions = dots * self.SFACTOR

        pos_a = (x1, y1 + 1)
        pos_b = (x2, y2 + 1)
        interp = self.dot_drawing_offset
        colour = (0, 255, 0) # brigt green dots

        self.dot_positions = [
            partial_vector.Partial_Vector(pos_a, pos_b, (interp, positions))
            for interp in range(self.dot_drawing_offset, positions,
                    self.SFACTOR) ]

        for pos in self.dot_positions:
            r.center = (int(pos[0]), int(pos[1]))
            output.fill(colour, r)

    # Tune these to alter the speed of the dots.
    SFACTOR = 512
    FUTZFACTOR = 4.0 * 35.0

    def Frame_Advance(self, frame_time: float) -> None:
        self.dot_drawing_offset += int(self.FUTZFACTOR *
                frame_time * self.current_n1_to_n2)

        if ( self.dot_drawing_offset < 0 ):
            self.dot_drawing_offset = (
                self.SFACTOR - (( - self.dot_drawing_offset ) % self.SFACTOR ))
        else:
            self.dot_drawing_offset = self.dot_drawing_offset % self.SFACTOR

    def Pre_Save(self) -> None:
        self.dot_positions = []

    def Draw_Selected(self, output: SurfaceType, highlight: Colour) -> Optional[RectType]:
        p1 = Grid_To_Scr(self.n1.pos)
        p2 = Grid_To_Scr(self.n2.pos)
        size5 = draw_effects.Get_Scaled_Size(5)
        size7 = draw_effects.Get_Scaled_Size(7)
        pygame.draw.line(output, highlight, p1, p2, size5)
        #self.Draw(output) # Already done elsewhere.

        return pygame.Rect(p1,(1,1)).union(pygame.Rect(p2,(1,1))).inflate(size7,size7)

    def Get_Information(self) -> List[StatTuple]:
        return Building.Get_Information(self) + [
            ((128,128,128), 15, "%1.1f km" % self.length) ,
            ((128,128,128), 15, "Flow rate: %1.1f U" % abs(self.current_n1_to_n2) ) ]

    def Sound_Effect(self) -> None:
        sound.FX(Sounds.bamboo2)


