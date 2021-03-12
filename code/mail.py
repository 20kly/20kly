#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, time, sys


from . import stats
from .game_types import *

MSG_MAX = 5
MSG_MARGIN = 5
MSG_EXPIRY_TIME = 20

class Message:
    def __init__(self, text: str, colour: Colour) -> None:
        self.text = text
        self.expiry_time = time.time() + MSG_EXPIRY_TIME
        self.colour = colour
        self.draw = stats.Get_Font(20).render(text, True, colour)
        self.undraw = pygame.Surface(self.draw.get_rect().size)
        self.area: RectType = pygame.Rect(0, 0, 1, 1)


class Mail:
    def __init__(self) -> None:
        self.messages: List[Message] = []
        self.day = 0
        self.change = True

    def Has_New_Mail(self) -> bool:

        # Limit number of on-screen messages
        while ( len(self.messages) > MSG_MAX ):
            self.messages.pop(0)
            self.change = True

        # Expire old messages
        cur_time = time.time()
        while (( len(self.messages) != 0 )
        and ( self.messages[ 0 ].expiry_time <= cur_time )):
            self.messages.pop(0)
            self.change = True

        x = self.change
        self.change = False
        return x

    def Draw_Mail(self, output: SurfaceType) -> None:
        # Show current messages
        y = output.get_rect().height - MSG_MARGIN

        for msg in reversed(self.messages):
            y -= msg.draw.get_rect().height

            r = msg.draw.get_rect()
            r.topleft = (MSG_MARGIN, y)
            msg.area = r
            output.blit(msg.draw, r.topleft)
            msg.undraw.blit(output.subsurface(r), (0, 0))

    def Undraw_Mail(self, output: SurfaceType) -> None:
        for msg in self.messages:
            output.blit(msg.undraw, msg.area.topleft)

    def New_Mail(self, text: str, colour: Colour = (128,128,128)) -> None:
        text = ( "Day %u: " % self.day ) + text
        self.messages.append(Message(text, colour))
        self.change = True
        print(text)
        sys.stdout.flush()

__mail = Mail()

def Initialise() -> None:
    global __mail
    __mail.messages = []
    __mail.day = 0
    __mail.change = True

def Set_Day(day: float) -> None:
    __mail.day = int(day)

def New_Mail(text: str, colour: Colour = (128,128,128)) -> None:
    __mail.New_Mail(text, colour)

def Has_New_Mail() -> bool:
    return __mail.Has_New_Mail()

def Draw_Mail(output: SurfaceType) -> None:
    __mail.Draw_Mail(output)

def Undraw_Mail(output: SurfaceType) -> None:
    __mail.Undraw_Mail(output)

def Get_Messages() -> str:
    return "\n".join([ m.text for m in __mail.messages ])


