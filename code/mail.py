#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame , time , sys


import stats
from game_types import *

__messages: List[MessageType] = []
__day = 0
__change = False

MSG_MAX = 5
MSG_MARGIN = 5
MSG_EXPIRY_TIME = 20

def Has_New_Mail() -> bool:
    global __messages, __change

    # Limit number of on-screen messages
    while ( len(__messages) > MSG_MAX ):
        __messages.pop(0)
        __change = True

    # Expire old messages
    cur_time = time.time()
    while (( len(__messages) != 0 )
    and ( __messages[ 0 ][ 0 ] <= cur_time )):
        __messages.pop(0)
        __change = True

    x = __change
    __change = False
    return x

def Draw_Mail(output: SurfaceType) -> None:
    # Show current messages
    y = output.get_rect().height - MSG_MARGIN

    for (tm, surf) in reversed(__messages):
        y -= surf.get_rect().height

        r = surf.get_rect()
        r.topleft = (MSG_MARGIN, y)
        output.blit(surf, r.topleft)


def Set_Day(day: float) -> None:
    global __day
    __day = int(day)

def New_Mail(text: str, colour: Colour = (128,128,128)) -> None:
    global __messages, __day, __change
    text = ( "Day %u: " % __day ) + text
    __messages.append((time.time() + MSG_EXPIRY_TIME,
            stats.Get_Font(20).render(text, True, colour)))
    __change = True
    print(text)
    sys.stdout.flush()

def Initialise() -> None:
    global __messages
    __messages = []
    __change = True



