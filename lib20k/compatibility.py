#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame


# Minimum supported pygame is 1.9
PYGAME_TWO = (pygame.version.vernum[0] >= 2)

# pygame < 2.0 doesn't provide an easy way to get the new window size after a resize
last_resize = (0, 0)

# Seems to be absent from older pygame versions (though it still works)
try:
    APPINPUTFOCUS = pygame.APPINPUTFOCUS
except AttributeError:  # NO-COV
    APPINPUTFOCUS = 2

# this function is not in pygame 1.9
try:
    set_allow_screensaver = pygame.display.set_allow_screensaver
except AttributeError:  # NO-COV
    set_allow_screensaver = lambda x: None
