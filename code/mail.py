#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, time, sys


from . import font
from .game_types import *
from .primitives import *

MSG_MAX = 5
MSG_MARGIN = 5
MSG_EXPIRY_TIME = 20

class Message:
    def __init__(self, text: str, colour: Colour) -> None:
        self.text = text
        self.expiry_time = time.time() + MSG_EXPIRY_TIME
        self.colour = colour
        self.area: RectType = pygame.Rect(0, 0, 1, 1)
        self.Render()

    def Render(self) -> None:
        # Text drawn in legacy size 20
        # This will be scaled for the current screen size within the font module.
        self.draw: SurfaceType = font.Get_Font(20).render(self.text, True, self.colour)
        self.undraw: SurfaceType = pygame.Surface((1, 1))

class Mail:
    def __init__(self) -> None:
        self.messages: List[Message] = []
        self.day = 0
        self.change = True

    def Render(self) -> None:
        # Render messages again after screen size change
        for msg in self.messages:
            msg.Render()

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
            msg.undraw = output.subsurface(r).copy()
            output.blit(msg.draw, r.topleft)

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

def Set_Screen_Height(height: int) -> None:
    """Notify components of a screen size change."""
    from . import grid, tutor, draw_effects
    font.Set_Screen_Height(height)
    grid.Set_Screen_Height(height)
    tutor.Set_Screen_Height(height)
    draw_effects.Set_Screen_Height(height)
    __mail.Render()

