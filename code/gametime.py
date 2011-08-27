# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 




class Game_Time:
    def __init__(self):
        self.__day = 0.0

    def Advance(self,step):
        self.__day += step

    def time(self):
        return self.__day

    def Get_Day(self):
        return int(self.__day)


