#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

import pickle, os, time, sys
from .game_types import *
from .primitives import *


class Config:
    def __init__(self) -> None:
        self.Reset()

    def Reset(self) -> None:
        self.version = VERSION
        self.mute = True
        self.test = 0
        self.width = MINIMUM_WIDTH
        self.height = MINIMUM_HEIGHT

cfg = Config()

FILENAME: Optional[str] = None

def Initialise(delete_file: bool) -> None:
    global cfg, FILENAME

    home = Get_Home()
    if ( home is None ):            # NO-COV
        FILENAME = "config.dat"     # NO-COV
    else:
        FILENAME = os.path.join(home, ".lightyears.cfg")

    if delete_file:
        # Don't load old configuration
        Save()
        return

    try:
        f = open(FILENAME, "rb")
        cfg2 = pickle.load(f)
        f.close()
        if ((cfg2.version[:2] == VERSION[:2])
        and (cfg2.width >= MINIMUM_WIDTH)
        and (cfg2.height >= MINIMUM_HEIGHT)):
            # Configuration is valid, we can use it.
            cfg = cfg2
    except Exception:
        pass

def Save() -> None:
    global cfg, FILENAME

    try:
        assert FILENAME
        f = open(FILENAME, "wb")
        pickle.dump(cfg, f)
        f.close()
    except Exception:
        pass

def Get_System_Info() -> str:
    # Some information about the run-time environment.
    # This gets included in savegames - it may be useful for
    # debugging problems using a savegame as a starting point.
    return repr([time.asctime(), sys.platform, sys.version,
            pygame.version.ver, sys.path, sys.prefix, sys.executable])


def Get_Home() -> Optional[str]:
    for i in [ "HOME", "APPDATA" ]:     # NO-COV
        home = os.getenv(i)             # NO-COV
        if ( home is not None ):        # NO-COV
            return home                 # NO-COV
    return None                         # NO-COV

