# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 


import pygame, os, sys
from pygame.locals import *

from mail import New_Mail
from primitives import *

__img_cache = dict()
__snd_cache = dict()
__snd_disabled = False

if not pygame.mixer or not pygame.mixer.get_init():
	__snd_disabled = True

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


def Path(name, audio=False):
    if ( audio ):
        return os.path.join(DATA_DIR,"..","audio",name)
    else:
        return os.path.join(DATA_DIR,name)

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


DEB_FONT = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
def Load_Font(size):
    # ----------------------------------------------------------
    # This function was modified by Siegfried Gevatter, the
    # maintainer of "lighyears" in Debian, to let lightyears
    # use the font from package "ttf-dejavu-core" instead of
    # it's own copy of it.
    #
    # Note: pygame.font.Font is used instead of pygame.font.SysFont
    # because with this last one the size of the text changed unexpectedly
    # ----------------------------------------------------------

    if os.path.isfile(DEB_FONT):
        return pygame.font.Font(DEB_FONT, size)

    return pygame.font.Font(Path("Vera.ttf"), size)

def Load_Sound(name):
    global __snd_cache, __snd_disabled
   
    if ( __snd_disabled ):
        return None

    if ( __snd_cache.has_key(name) ):
        return __snd_cache[ name ]

    #print "Caching new sound:",name
    fname = AUDIO_TRANS_TBL.get(name, name)
    fname = Path(fname + ".ogg", True)
    try:
        f = pygame.mixer.Sound(fname)
    except Exception, x:
        print ""
        print "WARNING: Error loading sound effect " + fname
        print "Real name: " + name
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


