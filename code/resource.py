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
__snd_cache: "Dict[Sounds, Optional[SoundType]]" = dict()
__snd_disabled = False

DATA_DIR = os.path.abspath(os.path.join(
                os.path.dirname(sys.argv[ 0 ]), "data"))


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

def Load_Sound(name: Sounds) -> "Optional[SoundType]":
    global __snd_cache, __snd_disabled

    if __snd_disabled:
        return None

    f: "Optional[SoundType]" = __snd_cache.get(name, None)
    if f is not None:  # NO-COV
        return f

    #print "Caching new sound:",name
    fname = Path(name.value + ".ogg", True)
    try:
        f = pygame.mixer.Sound(fname)
    except Exception as x:  # NO-COV
        print("")
        print("WARNING: Error loading sound effect " + fname)
        print(repr(x) + " " + str(x))
        print("")
        No_Sound()

    __snd_cache[ name ] = f

    return f


def Has_No_Sound() -> bool:
    return __snd_disabled

def No_Sound() -> None:
    global __snd_disabled
    __snd_disabled = True
