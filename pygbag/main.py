#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-26.
#

import pygame
from lib20k.main import Pygbag_Main

async def main() -> None:
    print(dir(pygame))
    print(dir(pygame.surface))
    await Pygbag_Main()
