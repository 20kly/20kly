# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

import pickle , startup


class Config:
    def __init__(self):
        # Default settings:
        self.version = startup.Get_Game_Version()
        self.resolution = (1024, 768)
        self.fullscreen = True
        self.font_scale = 4
        self.seen_before = False

cfg = Config()

FILENAME = "config.dat"

def Initialise():
    global cfg, FILENAME

    try:
        f = file(FILENAME, "rb")
        cfg2 = pickle.load(f)
        f.close()
        if ( cfg2.version == startup.Get_Game_Version() ):
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

