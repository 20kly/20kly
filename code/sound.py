#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


import pygame


from .primitives import *
from .game_types import *
from . import resource, config


VOL_SCALE = 0.8


def FX(name: Sounds) -> None:  # NO-COV
    s = resource.Load_Sound(name) # (comes from a cache)
    if ( s is not None ) and not config.cfg.mute:
        s.set_volume(VOL_SCALE)
        s.play()


class Persisting_Sound:
    def __init__(self, name: Sounds, secondary: Optional[Sounds] = None) -> None:
        self.sobj = resource.Load_Sound(name)
        if ( secondary is not None ):
            # A different, less annoying mode.
            self.sobj2 = resource.Load_Sound(secondary)
        else:
            self.sobj2 = self.sobj

        self.schan: Optional[pygame.Channel] = None

    def Set(self, volume: float) -> None:  # NO-COV
        if (( self.sobj is None )
        or ( self.sobj2 is None )):
            return

        if config.cfg.mute:
            volume = 0.0

        if ( volume <= 0.0 ):
            self.sobj.stop()
            self.sobj2.stop()
        else:
            self.sobj.set_volume(volume * VOL_SCALE)
            self.sobj2.set_volume(volume * VOL_SCALE)
            if (( self.schan is None )
            or ( not ( self.schan.get_sound()
                            in [ self.sobj , self.sobj2 ] ))):
                self.schan = self.sobj.play()
            if self.schan:
                self.schan.queue(self.sobj2)

    def Fade_Out(self) -> None:  # NO-COV
        if (( self.sobj is None )
        or ( self.sobj2 is None )
        or ( self.schan is None )):
            return

        self.schan.queue(self.sobj2)
        self.sobj2.fadeout(200)


