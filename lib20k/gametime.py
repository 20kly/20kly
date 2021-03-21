#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


from .game_types import *


class Game_Time:
    def __init__(self) -> None:
        self.__day = 0.0

    def Advance(self,step: float) -> None:
        self.__day += step

    def time(self) -> float:
        return self.__day

    def Get_Day(self) -> int:
        return int(self.__day)


