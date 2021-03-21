#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import pygame, os, sys, shutil


from .mail import New_Mail
from .primitives import *
from .game_types import *

try:
    SoundType = pygame.mixer.Sound  # pygame.mixer might not be available
except Exception:       # NO-COV
    pass


DATA_DIR = os.path.abspath(os.path.join(
                os.path.dirname(sys.argv[ 0 ]), "data"))

class MissingFileError(Exception):  # NO-COV
    def __init__(self, name: str) -> None:
        Exception.__init__(self, "Unable to find LightYears data file: {}".format(name))

def Path(name: str) -> str:
    return os.path.join(DATA_DIR, name)


class Resource:
    def __init__(self) -> None:
        self.img_cache: Dict[Images, SurfaceType] = dict()
        self.img_file: Dict[Images, str] = dict()
        self.snd_cache: "Dict[Sounds, SoundType]" = dict()
        self.snd_disabled = False

    def Load(self) -> None:
        # Use Debian font file if possible
        if os.path.isfile(DEB_FONT):  # NO-COV
            self.font_file = DEB_FONT
        else:
            self.font_file = Path("Vera_ttf")

        if not os.path.isfile(self.font_file):  # NO-COV
            raise MissingFileError(self.font_file)

        # Default locations for images
        for img_name in Images:
            self.img_file[img_name] = Path(img_name.value)

        # Use Debian icon file if possible
        if os.path.isfile(DEB_ICON):        # NO-COV
            self.img_file[Images.i32] = DEB_ICON

        # Load all images
        for img_name in Images:
            fname = self.img_file[img_name]
            if not os.path.isfile(fname):  # NO-COV
                raise MissingFileError(fname)

            self.img_cache[img_name] = pygame.image.load(fname) 

        # Load all sounds
        for snd_name in Sounds:
            if self.snd_disabled:
                break

            fname = Path(snd_name.value + "_ogg")
            if not os.path.isfile(fname):  # NO-COV
                raise MissingFileError(fname)

            try:
                self.snd_cache[snd_name] = pygame.mixer.Sound(fname)
            except Exception as x:  # NO-COV
                sys.stderr.write("Error loading sound effect {}: sound is disabled.\n"
                                 "More information: {} {}\n".format(snd_name, repr(x), str(x)))
                self.snd_disabled = True
                break


__resource = Resource()

def Load_Image(name: Images) -> SurfaceType:
    return __resource.img_cache[name]

def Load_Sound(name: Sounds) -> "Optional[SoundType]":
    return __resource.snd_cache.get(name, None)

def Load_Font(size: int) -> pygame.font.Font:
    return pygame.font.Font(__resource.font_file, size)

def Has_No_Sound() -> bool:
    return __resource.snd_disabled

def No_Sound() -> None:
    __resource.snd_disabled = True

def Initialise() -> None:
    __resource.Load()
