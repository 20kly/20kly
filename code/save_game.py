# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 

import pickle, extra, os


HEADER_SIZE = 100
NUM_SLOTS = 10

def Make_Save_Name(num):
    name = "save" + str(num) + ".dat"
    home = extra.Get_Home()
    if ( home == None ):
        return name
    else:
        return os.path.join(home, ".lightyears." + name)

def Load(g, num):
    name = Make_Save_Name(num)
    try:
        f = file(name, "rb")
        header = f.read( HEADER_SIZE )
        g2 = pickle.load(f)
        f.close()
    except Exception as x:
        y = ("Error restoring file: " + repr(x) + str(x))
        print(y)
        return (None, y)
    
    if ( g2.version != g.version ):
        return (None, "Restore error: wrong version")

    return (g2, None)
    
def Save(g, num, label):
    l = len(label)
    if ( l > HEADER_SIZE ):
        label = label[ 0:HEADER_SIZE ]
    else:
        label += ( " " * ( HEADER_SIZE - l ))

    name = Make_Save_Name(num)
    try:
        f = file(name, "wb")
        f.write(label)
        pickle.dump(g,f)
        f.close()
    except Exception as x:
        return "Error saving file: " + repr(x) + str(x)
    
    return None

def Get_Info(num):
    name = Make_Save_Name(num)
    label = ""
    try:
        f = file(name, "rb")
        label = f.read( HEADER_SIZE )
        f.close()
    except Exception as x:
        # File not found, probably.. who cares.
        return None

    if ( len(label) == 0 ):
        return None
    return label


