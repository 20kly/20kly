# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


import pygame , os
from pygame.locals import *

from mail import New_Mail
from primitives import *

__img_cache = dict()
__snd_cache = dict()
__snd_disabled = False



def Path(name, audio=False):
    if ( audio ):
        return os.path.join("data","audio",name)
    else:
        return os.path.join("data",name)

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
    fname = Path("font.ttf")
    try:
        f = pygame.font.Font(fname, size)
    except Exception, x:
        print ""
        print "WARNING: Error loading custom font - falling back to system font"
        print repr(x) + " " + str(x)
        print ""
        f = pygame.font.SysFont(None, size)
    
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


