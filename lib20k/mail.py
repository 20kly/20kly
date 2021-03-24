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
MSG_EXPIRY_TIME = 200

class Message:
    def __init__(self, text: str, colour: Colour) -> None:
        self.text = text
        self.expiry_countdown = MSG_EXPIRY_TIME
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

    def Render(self) -> None:
        # Render messages again after screen size change
        for msg in self.messages:
            msg.Render()

    def Expire_Messages(self) -> None:
        # All messages tick downwards
        for msg in self.messages:
            msg.expiry_countdown -= 1

        # Limit number of on-screen messages
        while ( len(self.messages) > MSG_MAX ):
            self.messages.pop(0)

        # Remove expired messages
        while ((len(self.messages) != 0) and (self.messages[0].expiry_countdown <= 0)):
            self.messages.pop(0)

    def Draw_Mail(self, output: SurfaceType) -> None:
        # Show current messages
        sr = output.get_rect()
        y = sr.height - MSG_MARGIN

        for msg in reversed(self.messages):
            y -= msg.draw.get_rect().height

            r = msg.draw.get_rect()
            r.topleft = (MSG_MARGIN, y)
            r = r.clip(sr)
            msg.area = r
            msg.undraw = output.subsurface(r).copy()
            output.blit(msg.draw, r.topleft)

    def Undraw_Mail(self, output: SurfaceType) -> None:
        for msg in self.messages:
            output.blit(msg.undraw, msg.area.topleft)

    def New_Mail(self, text: str, colour: Colour = (128,128,128)) -> None:
        text = ( "Day %u: " % self.day ) + text
        self.messages.append(Message(text, colour))
        print(text)
        sys.stdout.flush()

__mail = Mail()

def Initialise() -> None:
    __mail.messages = []
    __mail.day = 0

def Set_Day(day: float) -> None:
    __mail.day = int(day)

def New_Mail(text: str, colour: Colour = (128,128,128)) -> None:
    __mail.New_Mail(text, colour)

def Expire_Messages() -> None:
    __mail.Expire_Messages()

def Draw_Mail(output: SurfaceType) -> None:
    __mail.Draw_Mail(output)

def Undraw_Mail(output: SurfaceType) -> None:
    __mail.Undraw_Mail(output)

def Get_Messages() -> str:
    return "\n".join([ m.text for m in __mail.messages ])

def Set_Screen_Height(height: int) -> None:
    """Notify components of a screen size change."""
    from . import grid, tutor, draw_effects, storms
    font.Set_Screen_Height(height)
    grid.Set_Screen_Height(height)
    tutor.Set_Screen_Height(height)
    storms.Set_Screen_Height(height)
    draw_effects.Set_Screen_Height(height)
    __mail.Render()

