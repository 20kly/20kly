# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

import pickle, os
import startup, extra

CFG_VER = startup.Get_Game_Version() + "/newui"

class Config:
    def __init__(self):
        # Default settings:
        self.version = CFG_VER
        self.resolution = (1024, 768)
        self.fullscreen = False
        self.font_scale = 4
        self.seen_before = False
        self.mute = True

cfg = Config()
FILENAME = None
DATA_DIR = "invalid"

def Initialise(data_dir, delete_file):
    global cfg, FILENAME, DATA_DIR

    DATA_DIR = data_dir

    home = extra.Get_Home()
    if home == None:
        FILENAME = "config.dat"
    else:
        FILENAME = os.path.join(home, ".lightyears.cfg")

    if delete_file:
        # Don't load old configuration
        Save()
        return

    try:
        f = file(FILENAME, "rb")
        cfg2 = pickle.load(f)
        f.close()
        if ( cfg2.version == CFG_VER ):
            # Configuration is valid, we can use it.
            cfg = cfg2
    except Exception, x:
        pass

def Save():
    global cfg, FILENAME

    try:
        f = file(FILENAME, "wb")
        pickle.dump(cfg, f)
        f.close()
    except Exception, x:
        pass

