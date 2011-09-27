# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


import pygame, os, sys
from pygame.locals import *

from mail import New_Mail
from primitives import *
import config

__img_cache = dict()
__snd_cache = dict()
__snd_disabled = False

DEB_FONT = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"

def Path(name, audio=False):
    if ( audio ):
        return os.path.join(config.DATA_DIR, os.path.pardir, "audio", name)
    else:
        return os.path.join(config.DATA_DIR, name)

def Load_Image(name):
    global __img_cache

    key = name

    if ( __img_cache.has_key(key) ):
        return __img_cache[ key ]

    fname = Path(name)
    try:
        img = pygame.image.load(fname)
    except Exception, r:
        s = "WARNING: Unable to load image '" + fname + "': " + str(r)
        print ""
        print s
        print ""
        New_Mail(s)
        img = pygame.Surface((10,10))
        img.fill((255,0,0))

    i = __img_cache[ key ] = img.convert_alpha()
    return i


def Load_Font(size):
    if os.path.isfile(DEB_FONT):
        # Siegfried Gevatter's recommendation - use font from
        # ttf-dejavu-core package if available
        return pygame.font.Font(DEB_FONT, size)

    # Otherwise use my own copy
    fname = Path("DejaVuSans.ttf")
    try:
        f = pygame.font.Font(fname, size)
    except Exception, x:
        # And if that fails...
        print ""
        print "ERROR: Error loading custom font"
        sys.exit(1)

    return f

def Load_Sound(name):
    global __snd_cache, __snd_disabled
   
    if ( __snd_disabled ):
        return None

    if ( __snd_cache.has_key(name) ):
        return __snd_cache[ name ]

    #print "Caching new sound:",name
    fname = Path(name + ".wav", True)
    try:
        f = pygame.mixer.Sound(fname)
    except Exception, x:
        print ""
        print "WARNING: Error loading sound effect " + fname
        print repr(x) + " " + str(x)
        print ""
        f = None
   
    __snd_cache[ name ] = f

    return f


def No_Sound():
    global __snd_disabled
    __snd_disabled = True

def Has_Sound():
    global __snd_disabled
    return not __snd_disabled 

