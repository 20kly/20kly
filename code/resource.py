#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, os, sys


from .mail import New_Mail
from .primitives import *
from .game_types import *

try:
    SoundType = pygame.mixer.Sound  # pygame.mixer might not be available
except Exception:       # NO-COV
    pass

__img_cache: Dict[str, SurfaceType] = dict()
__snd_cache: "Dict[str, Optional[SoundType]]" = dict()
__snd_disabled = False

DATA_DIR = os.path.abspath(os.path.join(
                os.path.dirname(sys.argv[ 0 ]), "data"))

AUDIO_TRANS_TBL = {
    "bamboo" : "ack1",          # ack 1
    "bamboo1" : "ack2",         # ack 2
    "bamboo2" : "ack3",         # ack 3
    "crisp" : "ack4",           # ack 4
    "destroy" : "ack5",         # ack 5
    "double" : "ack6",          # ack 6
    "mechanical_1" : "ack7",    # ack 7
    "ring" : "ack8",            # ack 8
    "whoosh1" : "ack9",         # ack 9
    "applause" : "dack1",       # double ack 1
    "computer" : "dack2",       # double ack 2
    "emergency" : "alert1",     # emergency tone 1
    "firealrm" : "alert3",      # emergency tone 2
    "stormbeeps" : "alert2",    # emergency tone 3
    "clicker" : "aliens",       # alien noise
}


def Path(name: str, audio=False) -> str:
    if ( audio ):
        return os.path.join(DATA_DIR,"..","audio",name)
    else:
        return os.path.join(DATA_DIR,name)

def Load_Image(name: str) -> SurfaceType:
    global __img_cache

    key = name

    if ( __img_cache.get(key, None) ):
        return __img_cache[ key ]

    fname = Path(name)
    try:
        img = pygame.image.load(fname)
    except Exception as r:  # NO-COV
        s = "WARNING: Unable to load image '" + fname + "': " + str(r)
        print("")
        print(s)
        print("")
        New_Mail(s)
        img = pygame.Surface((10,10))
        img.fill((255,0,0))

    i = __img_cache[ key ] = img.convert_alpha()
    return i


def Load_Font(size: int) -> pygame.font.Font:
    # ----------------------------------------------------------
    # This function was modified by Siegfried Gevatter, the
    # maintainer of "lighyears" in Debian, to let lightyears
    # use the font from package "ttf-dejavu-core" instead of
    # it's own copy of it.
    #
    # Note: pygame.font.Font is used instead of pygame.font.SysFont
    # because with this last one the size of the text changed unexpectedly
    # ----------------------------------------------------------

    if os.path.isfile(DEB_FONT):  # NO-COV
        return pygame.font.Font(DEB_FONT, size)

    return pygame.font.Font(Path("Vera.ttf"), size)

def Load_Sound(name: str) -> "Optional[SoundType]":
    global __snd_cache, __snd_disabled

    if ( __snd_disabled ):
        return None

    f: "Optional[SoundType]" = __snd_cache.get(name, None)
    if f is not None:  # NO-COV
        return f

    #print "Caching new sound:",name
    fname = AUDIO_TRANS_TBL.get(name, name)
    fname = Path(fname + ".ogg", True)
    try:
        f = pygame.mixer.Sound(fname)
    except Exception as x:  # NO-COV
        print("")
        print("WARNING: Error loading sound effect " + fname)
        print("Real name: " + name)
        print(repr(x) + " " + str(x))
        print("")
        No_Sound()

    __snd_cache[ name ] = f

    return f


def No_Sound() -> None:
    global __snd_disabled
    __snd_disabled = True
