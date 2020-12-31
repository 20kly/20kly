# USE WITH CARE.

import save_game , startup , pickle

HEADER_SIZE = save_game.HEADER_SIZE

def Upgrade(num):
    name = save_game.Make_Save_Name(num)
    f = file(name, "rb")
    header = f.read( HEADER_SIZE )
    g2 = pickle.load(f)
    f.close()

    print 'current version:',g2.version
    g2.version = startup.Get_Game_Version()
    print 'new version:',g2.version

    save_game.Save(g2, num, header)

Upgrade(7)

