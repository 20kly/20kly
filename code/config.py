#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#

import pickle, startup, os, extra, primitives
from game_types import *


class Config:
    def __init__(self) -> None:
        self.version = startup.Get_Game_Version()
        self.mute = True
        self.seen_before = False

cfg = Config()

FILENAME: Optional[str] = None

def Initialise(delete_file: bool) -> None:
    global cfg, FILENAME

    version = startup.Get_Game_Version()
    home = extra.Get_Home()
    if ( home is None ):
        FILENAME = "config.dat"
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
        if cfg2.version == version:
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

