#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

# A model for the movement of steam within the system.


from .primitives import *
from .game_types import *
from . import network


class Steam_Model:
    # Don't understand steam? Confused by the thought of
    # boiling water being used as a source of energy?
    # Why not just assume that it's electricity.

    def __init__(self) -> None:
        # Invariant:
        self.capacitance = 1.0
        # May change:
        self.charge = 0.0
        self.voltage = 0.0
        # Changed by upgrades
        self.capacity = INITIAL_NODE_CAPACITY

    TIME_CONSTANT = 0.1
    NEGLIGIBLE = 0.01

    def Source(self, current: float) -> None:
        dq = current * self.TIME_CONSTANT
        self.charge += dq
        self.__Bound()

    def Think(self, neighbour_list: "List[Tuple[Steam_Model, float]]",
              net: network.Network) -> List[float]:
        self.voltage = self.charge / self.capacitance
        currents = []

        for (neighbour, resist) in neighbour_list:
            dir = 0
            # Potential difference:
            dv = self.voltage - neighbour.voltage
            if ( dv >= self.NEGLIGIBLE ):
                # Current flow:
                i = dv / resist
                # Charge flow:
                dq = i * self.TIME_CONSTANT
                self.charge -= dq
                neighbour.charge += dq
                currents.append(i)
            else:
                currents.append(0.0)

        self.__Bound()
        net.demo.Steam(neighbour_list, self.voltage, self.charge, self.capacitance, currents)
        return currents

    def __Bound(self) -> None:
        if ( self.charge < 0 ):
            self.charge = 0
        elif ( self.charge > self.capacity ):
            self.charge = self.capacity # vent

    def Get_Pressure(self) -> float:
        return self.charge

    def Get_Capacity(self) -> float:
        return self.capacity

    def Capacity_Upgrade(self) -> None:
        self.capacity += CAPACITY_UPGRADE
