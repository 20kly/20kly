#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

from .game_types import *
from . import network

class Quiet_Season:
    # The quiet season is... very quiet.
    def __init__(self, net: "network.Network") -> None:
        self.net = net
        self.name = "Quiet"

    def Per_Frame(self, frame_time: float) -> None:
        pass

    def Per_Period(self) -> None:
        pass

    def Draw(self, output: SurfaceType, update_area: UpdateAreaMethod) -> None:
        pass

    def Get_Period(self) -> int:
        return 10

    def Get_Extra_Info(self) -> List[StatTuple]:
        return []

    def Is_Shaking(self) -> bool:
        return False


