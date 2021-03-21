#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

from .primitives import *

# things that are set by the difficulty mode:
class Difficulty:
    def __init__(self) -> None:
        self.Set(MenuCommand.INTERMEDIATE)

    def Set(self, level: MenuCommand) -> None:
        if ( level in [ MenuCommand.BEGINNER , MenuCommand.TUTORIAL ] ):
            self.DAMAGE_FACTOR = 1.0
            self.CITY_UPGRADE_WORK_PER_LEVEL = 2
            self.GRACE_TIME = 20
            self.CITY_MAX_TECH_LEVEL = 9
            self.BASIC_STEAM_PRODUCTION = 10
            self.STEAM_PRODUCTION_PER_LEVEL = 6

        elif ( level in [ MenuCommand.INTERMEDIATE, MenuCommand.PEACEFUL ] ):
            self.DAMAGE_FACTOR = 1.4
            self.CITY_UPGRADE_WORK_PER_LEVEL = 3
            self.GRACE_TIME = 10
            self.CITY_MAX_TECH_LEVEL = 12
            self.BASIC_STEAM_PRODUCTION = 6
            self.STEAM_PRODUCTION_PER_LEVEL = 4

        else:
            assert level == MenuCommand.EXPERT
            self.DAMAGE_FACTOR = 1.7
            self.CITY_UPGRADE_WORK_PER_LEVEL = 4
            self.GRACE_TIME = 5
            self.CITY_MAX_TECH_LEVEL = 15
            self.BASIC_STEAM_PRODUCTION = 4
            self.STEAM_PRODUCTION_PER_LEVEL = 3

DIFFICULTY = Difficulty()

